from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated


from apps.accounts.permissions import IsParent

from .models import Subscription, Payment, PayPalPayment, AppVersion


import requests
from .paypal_api import get_access_token
from .paypal_config import PAYPAL_API_BASE
from packaging import version
# Payments methods 
import uuid
import os
from  .mtnmomo.get_mtn_access_token import get_mtn_access_token_api
from .models import MobileMoneyPayment, OrangeMoneyPayment
from  .orangemoney.get_om_access_token import get_om_access_token

@api_view(['GET'])
def check_version(request):
    platform = request.GET.get('platform')
    version_str = request.GET.get('version')

    if platform not in ['android', 'ios']:
        return Response({"detail": "Invalid platform."}, status=400)

    app_version = AppVersion.objects.filter(platform=platform).order_by('-created_at').first()

    if not app_version:
        return Response({"detail": "No version information available."}, status=404)

    try:
        # Convertir les versions en objets version pour une comparaison correcte
        current_version = version.parse(app_version.minimum_required_version)
        input_version = version.parse(version_str)

        if input_version < current_version:
            return Response({
                "update_required": True,
                "update_url": app_version.update_url,
            })
    except ValueError:
        return Response({"detail": "Invalid version format."}, status=400)

    return Response({"update_required": False})



    
# Paypal paiement views
class CreatePayPalPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        parent = request.user
        student_id = request.data.get('student_id')
        num_months = request.data.get('num_months')

        price_per_month = 20000
        total_price = price_per_month * num_months / 10000  # Convertir en USD

        student = get_object_or_404(Student, id=student_id)

        # Obtenir le jeton d'accès PayPal
        access_token = get_access_token()

        # Créer l'ordre PayPal
        order_response = requests.post(
            f'{PAYPAL_API_BASE}/v2/checkout/orders',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            json={
                'intent': 'CAPTURE',
                'purchase_units': [
                    {
                        'amount': {
                            'currency_code': 'USD',
                            'value': str(total_price),
                        }
                    }
                ]
            }
        )
        order_response.raise_for_status()
        order_data = order_response.json()

        # Créer le paiement
        payment = Payment.objects.create(
            parent=parent,
            student=student,
            payment_method='paypal',
            num_months=num_months,
            amount=total_price,
            status='pending'
        )

        # Créer les détails du paiement PayPal
        paypal_payment = PayPalPayment.objects.create(
            payment=payment,
            paypal_order_id=order_data['id']
        )

        return Response({'orderID': order_data['id']}, status=status.HTTP_201_CREATED)

class CapturePayPalPaymentView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')

        access_token = get_access_token()

        capture_response = requests.post(
            f'{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
        )
        capture_response.raise_for_status()

        paypal_payment = get_object_or_404(PayPalPayment, paypal_order_id=order_id)
        payment = paypal_payment.payment
        payment.status = 'completed'
        payment.save()

        # Calculer les dates de début et de fin
        start_date = timezone.now().date()
        end_date = start_date
        for _ in range(payment.num_months):
            end_date = get_end_of_month(end_date)
            end_date += timedelta(days=1)
        end_date -= timedelta(days=1)

        # Créer la souscription après le paiement réussi
        subscription = Subscription.objects.create(
            parent=payment.parent,
            student=payment.student,
            num_months=payment.num_months,
            amount=payment.amount,
            start_date=start_date,
            end_date=end_date,
            payment_method='paypal',
            status=True
        )

        payment.subscription = subscription
        payment.save()

        # Envoyer les notifications après la souscription
        parent = subscription.parent
        student = subscription.student

        notifications = Notification.objects.filter(student=student)
        for notification in notifications:
            UserNotification.objects.get_or_create(
                user=parent,
                notification=notification,
                student=student
            )

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class UnpaidMonthsView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def get(self, request, student_id):
        parent = request.user
        student = get_object_or_404(Student, id=student_id)

        # Obtenir toutes les dates de notifications envoyées pour l'élève
        notifications_sent = Notification.objects.filter(student=student)
        notifications_received = UserNotification.objects.filter(user=parent, student=student).values('notification__date')

        # Obtenir les mois uniques des notifications envoyées et reçues
        months_sent = {notification.date.strftime('%Y-%m') for notification in notifications_sent}
        months_received = {notification['notification__date'].strftime('%Y-%m') for notification in notifications_received}

        # Calculer le nombre de mois impayés par défaut
        num_unpaid_months = len(months_sent - months_received)

        # Obtenir la dernière souscription
        last_subscription = Subscription.objects.filter(parent=parent, student=student).order_by('-end_date').first()
        subscription_status = 'inactive'
        if last_subscription and last_subscription.status:
            subscription_status = 'active'
            # Réinitialiser le nombre de mois impayés si la souscription est active
            num_unpaid_months = 0
        else:
            # Si la souscription est expirée, recalculer les mois impayés
            if last_subscription:
                last_subscription_end_date = last_subscription.end_date.strftime('%Y-%m')
                # Filtrer les notifications envoyées après la fin de la dernière souscription
                months_sent_after_subscription = {notification.date.strftime('%Y-%m') for notification in notifications_sent if notification.date.strftime('%Y-%m') > last_subscription_end_date}
                num_unpaid_months = len(months_sent_after_subscription - months_received)

        # Obtenir la date de la première notification envoyée
        first_notification = notifications_sent.order_by('date').first()
        first_notification_date = first_notification.date if first_notification else None

        return Response({
            'unpaid_months': num_unpaid_months,
            'subscription_status': subscription_status,
            'first_notification_date': first_notification_date
        }, status=status.HTTP_200_OK)

# MTN MoMo
@api_view(['POST'])
def initier_paiement(request):
    parent = request.user
    student_id = request.data.get('student_id')
    num_months = request.data.get('num_months')

    numero_de_telephone = request.data.get("numero_de_telephone")
    reference_id = str(uuid.uuid4())

    # Calcul du montant
    price_per_month = 20000  # 20000 par mois
    total_price = num_months * price_per_month

    student = get_object_or_404(Student, id=student_id)

    # Créer le paiement
    payment = Payment.objects.create(
        parent=parent,
        student=student,
        payment_method='mobile_money',
        num_months=num_months,
        amount=total_price,
        status='pending'
    )
    
    url = "https://proxy.momoapi.mtn.com/collection/v1_0/requesttopay"
    headers = {
        "Authorization": f"Bearer {get_mtn_access_token_api()}",
        "X-Reference-Id": reference_id,
        "X-Target-Environment": "mtnguineaconakry",
        "Ocp-Apim-Subscription-Key": os.getenv("MTN_SUBSCRIPTION_KEY"),
        "Content-Type": "application/json"
    }
    body = {
        "amount": total_price,
        "currency": "GNF",
        "externalId": str(uuid.uuid4()),
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": numero_de_telephone
        },
        "payerMessage": "Souscription school liaison guinee",
        "payeeNote": "Merci de votre confiance"
    }
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 202:
        # Enregistrer les détails du paiement MTN
        MobileMoneyPayment.objects.create(payment=payment, reference_id=reference_id)
        return Response({"message": "Paiement initié avec succès", "reference_id": reference_id})
    else:
        payment.status = 'failed'
        payment.save()
        return Response(response.text, status=response.status_code)
    
def check_payment_status(reference_id):
    url = f"https://proxy.momoapi.mtn.com/collection/v1_0/requesttopay/{reference_id}"
    headers = {
        "Authorization": f"Bearer {get_mtn_access_token_api()}",
        "Ocp-Apim-Subscription-Key": os.getenv("MTN_SUBSCRIPTION_KEY"),
        "X-Target-Environment": "mtnguineaconakry",
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        mtn_payment = get_object_or_404(MobileMoneyPayment, reference_id=reference_id)
        payment = mtn_payment.payment

        if data['status'] == 'SUCCESSFUL':
            payment.status = 'completed'
            payment.save()

            # Vérifier si une souscription existe déjà pour ce paiement
            if not payment.subscription:
                # Calcul des dates de souscription
                start_date = payment.created_at.date()
                end_date = start_date
                for _ in range(payment.num_months):
                    end_date = get_end_of_month(end_date)
                    end_date += timedelta(days=1)
                end_date -= timedelta(days=1)

                # Création de la souscription
                subscription = Subscription.objects.create(
                    parent=payment.parent,
                    student=payment.student,
                    num_months=payment.num_months,
                    amount=payment.amount,
                    start_date=start_date,
                    end_date=end_date,
                    payment_method='mobile_money',
                    status=True
                )

                payment.subscription = subscription
                payment.save()

                # Envoyer les notifications après la souscription
                parent = subscription.parent
                student = subscription.student

                notifications = Notification.objects.filter(student=student)
                for notification in notifications:
                    UserNotification.objects.get_or_create(
                        user=parent,
                        notification=notification,
                        student=student
                    )

        elif data['status'] == 'FAILED':
            payment.status = 'failed'
            payment.save()

    return response.status_code, data

@api_view(['GET'])
def get_last_mobile_money_payment(request, student_id):
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Récupérer l'étudiant
        student = Student.objects.get(id=student_id)
        
        # Récupérer le dernier paiement Mobile Money pour ce parent et cet étudiant
        payment = Payment.objects.filter(student=student, parent=request.user, payment_method='mobile_money').order_by('-created_at').first()
        
        if payment:
            mtn_payment = MobileMoneyPayment.objects.get(payment=payment)
            created_date = payment.created_at.date() 
            
            # Vérifier le statut du paiement
            status_code, data = check_payment_status(mtn_payment.reference_id)
            
            return Response({
                "reference_id": mtn_payment.reference_id,
                "created_at": created_date,
                "payment_status": data['status']
            })
        else:
            return Response({"detail": "No Mobile Money payment found for this student."}, status=status.HTTP_404_NOT_FOUND)
    
    except Student.DoesNotExist:
        return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except MobileMoneyPayment.DoesNotExist:
        return Response({"detail": "Mobile Money payment details not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def verifier_statut_paiement(request, reference_id):
    status_code, data = check_payment_status(reference_id)
    if status_code == 200:
        return Response(data)
    else:
        return Response(data, status=status_code)

# Orange money
@api_view(['POST'])
def initier_paiement_orange(request):
    parent = request.user
    student_id = request.data.get('student_id')
    num_months = request.data.get('num_months')

    order_id = str(uuid.uuid4())

    # Calcul du montant
    price_per_month = 1000  # 20000 GNF par mois
    total_price = num_months * price_per_month

    student = get_object_or_404(Student, id=student_id)

    # Créer le paiement
    payment = Payment.objects.create(
        parent=parent,
        student=student,
        payment_method='orange_money',
        num_months=num_months,
        amount=total_price,
        status='pending'
    )
    
    # url = "https://api.orange.com/orange-money-webpay/gn/v1/webpayment" # url for prod
    url = "https://api.orange.com/orange-money-webpay/dev/v1/webpayment" # url for dev

    headers = {
        "Authorization": f"Bearer {get_om_access_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    body = {
        "merchant_key": f"{os.getenv('OM_MERCHANT_KEY')}",
        "currency": "OUV", # GNF for prod or OUV for dev
        "order_id": order_id,
        "amount": total_price,
        "return_url": "https://api.schoolliaisonguinee.com/school-liaison/api/om/payment/return",
        "cancel_url": "https://api.schoolliaisonguinee.com/school-liaison/api/om/payment/cancel",
        "notif_url": "https://api.schoolliaisonguinee.com/school-liaison/api/om/payment/notification",
        "lang": "fr",
        "reference": "souscription.school.liaison"
    }

    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 201:
        payment_data = response.json()
        OrangeMoneyPayment.objects.create(
            payment=payment, 
            order_id=order_id, 
            pay_token=payment_data["pay_token"],
            payment_url=payment_data["payment_url"],
            notif_token=payment_data["notif_token"]
        )
        return Response({"message": "Paiement initié avec succès", "payment_url": payment_data["payment_url"]})
    else:
        payment.status = 'failed'
        payment.save()
        return Response(response.text, status=response.status_code)

def payment_success(request):
    return Response({"message": "Votre paiement a été effectué avec succès."})

def payment_cancel(request):
    return Response({"message": "Votre paiement a été annulé."})

@api_view(['POST'])
def payment_notification(request):
    notif_token = request.data.get('notif_token')
    payment_status = request.data.get('status')
    txnid = request.data.get('txnid')

    # Valider le token
    orange_payment  = get_object_or_404(OrangeMoneyPayment, notif_token=notif_token)
    payment = orange_payment.payment

    if payment_status == 'SUCCESS':
        payment.status = 'completed'
        payment.save()

        # Vérifier si une souscription existe déjà pour ce paiement
        if not payment.subscription:
            # Calcul des dates de souscription
            start_date = payment.created_at.date()
            end_date = start_date
            for _ in range(payment.num_months):
                end_date = get_end_of_month(end_date)
                end_date += timedelta(days=1)
            end_date -= timedelta(days=1)

            # Création de la souscription
            subscription = Subscription.objects.create(
                parent=payment.parent,
                student=payment.student,
                num_months=payment.num_months,
                amount=payment.amount,
                start_date=start_date,
                end_date=end_date,
                payment_method='orange_money',
                status=True
            )

            payment.subscription = subscription
            payment.save()

            # Envoyer les notifications après la souscription
            parent = subscription.parent
            student = subscription.student

            notifications = Notification.objects.filter(student=student)
            for notification in notifications:
                UserNotification.objects.get_or_create(
                    user=parent,
                    notification=notification,
                    student=student
                )

        else:
            payment.status = 'failed'
            payment.save()

    return Response({"message": "Notification traitée avec succès"})

