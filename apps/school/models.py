from django.db import models

from django.dispatch import receiver
from django.db.models.signals import post_save


# from django.contrib.auth import get_user_model
# from apps.accounts.models import User
# User = get_user_model()

# School Year Model
class SchoolYear(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.start_date.year}-{self.end_date.year}"

    class Meta:
        verbose_name_plural = "0. School Years"

# School Model 
class School(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    agent = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.agent}"
    
    class Meta:
        verbose_name_plural = "2. School"

# Classe Model 
class Classe(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    level = models.CharField(max_length=100,choices=[
        ('primaire', 'Primaire'),
        ('college', 'Collège'),
        ('lycee', 'Lycée')
    ])
    name = models.CharField(max_length=100,choices=[
        ('1ere Annee A', '1ère Année A'),
        ('1ere Annee B', '1ère Année B'),
        ('1ere Annee C', '1ère Année C'),
        ('2eme Annee A', '2ème Année A'),
        ('2eme Annee B', '2ème Année B'),
        ('2eme Annee C', '2ème Année C'),
        ('3eme Annee A', '3ème Année A'),
        ('3eme Annee B', '3ème Année B'),
        ('3eme Annee C', '3ème Année C'),
        ('4eme Annee A', '4ème Année A'),
        ('4eme Annee B', '4ème Année B'),
        ('4eme Annee C', '4ème Année C'),
        ('5eme Annee A', '5ème Année A'),
        ('5eme Annee B', '5ème Année B'),
        ('5eme Annee C', '5ème Année C'),
        ('6eme Annee A', '6ème Année A'),
        ('6eme Annee B', '6ème Année B'),
        ('6eme Annee C', '6ème Année C'),
        ('7eme Annee A', '7ème Année A'),
        ('7eme Annee B', '7ème Année B'),
        ('7eme Annee C', '7ème Année C'),
        ('8eme Annee A', '8ème Année A'),
        ('8eme Annee B', '8ème Année B'),
        ('8eme Annee C', '8ème Année C'),
        ('9eme Annee A', '9ème Année A'),
        ('9eme Annee B', '9ème Année B'),
        ('9eme Annee C', '9ème Année C'),
        ('10eme Annee A', '10ème Année A'),
        ('10eme Annee B', '10ème Année B'),
        ('10eme Annee C', '10ème Année C'),
        ('11eme S Litteraire 1', '11ème S Littéraire 1'),
        ('11eme S Litteraire 2', '11ème S Littéraire 2'),
        ('11eme S Litteraire 3', '11ème S Littéraire 3'),
        ('11eme S Scientifique 1', '11ème S Scientifique 1'),
        ('11eme S Scientifique 2', '11ème S Scientifique 2'),
        ('11eme S Scientifique 3', '11ème S Scientifique 3'),
        ('12eme S Litteraire 1', '12ème S Littéraire 1'),
        ('12eme S Litteraire 2', '12ème S Littéraire 2'),
        ('12eme S Litteraire 3', '12ème S Littéraire 3'),
        ('12eme S Scientifique 1', '12ème S Scientifique 1'),
        ('12eme S Scientifique 2', '12ème S Scientifique 2'),
        ('12eme S Scientifique 3', '12ème S Scientifique 3'),
        ('T SS 1', 'T SS 1'),
        ('T SS 2', 'T SS 2'),
        ('T SS 3', 'T SS 3'),
        ('T SE 1', 'T SE 1'),
        ('T SE 2', 'T SE 2'),
        ('T SE 3', 'T SE 3'),
        ('T SM 1', 'T SM 1'),
        ('T SM 2', 'T SM 2'),
        ('T SM 3', 'T SM 3'),
    ])
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.school}"
    
    class Meta:
        verbose_name_plural = "3. Classe" 

# Student Model
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    matricule = models.CharField(max_length=100, null=True, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True, default="default.jpg")
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"
    
    # def get_active_subscriptions(self):
    #     return self.subscription_set.filter(status='completed', end_date__gte=timezone.now().date())
    
    @property
    def classe_infos(self):
        classe_infos = self.classe
        return classe_infos
    
    class Meta:
        verbose_name_plural = "4. Student"

# Head Teacher Model
class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length = 100)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.classe} {self.phone}" 
    
    @property
    def classe_infos(self):
        classe_infos = self.classe  
        return classe_infos
    
    class Meta:
        verbose_name_plural = "5. Teacher"

def get_end_of_month(start_date):
    next_month = start_date.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


# Student Statistics Model
class StudentStatistics(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)
    absence = models.IntegerField(default=0)
    absence_autorisee = models.IntegerField(default=0)
    presence = models.IntegerField(default=0)
    mauvaise_conduite = models.IntegerField(default=0)
    bonne_conduite = models.IntegerField(default=0)
    participation_active = models.IntegerField(default=0)
    participation_moyenne = models.IntegerField(default=0)
    participation_faible = models.IntegerField(default=0)
    bonne_moyenne = models.IntegerField(default=0)
    mauvaise_moyenne = models.IntegerField(default=0)

    def __str__(self):
        return f"Statistiques de {self.student} pour {self.school_year}"

    class Meta:
        verbose_name_plural = "8. Student Statistics"
        unique_together = ('student', 'school_year')

# Signal pour mettre à jour les statistiques après la sauvegarde d'une notification
# @receiver(post_save, sender=Notification)
# def update_student_statistics(sender, instance, created, **kwargs):
#     if created:
#         statistics, _ = StudentStatistics.objects.get_or_create(
#             student=instance.student,
#             school_year=instance.school_year
#         )
#         for category in instance.categories.all():
#             if category.name == "présence en classe":
#                 statistics.presence += 1
#             elif category.name == "absence en classe":
#                 statistics.absence += 1
#             elif category.name == "absence autorisée":
#                 statistics.absence_autorisee += 1
#             elif category.name == "bonne conduite à l'école":
#                 statistics.bonne_conduite += 1
#             elif category.name == "mauvaise conduite à l'école":
#                 statistics.mauvaise_conduite += 1
#             elif category.name == "participation active en classe":
#                 statistics.participation_active += 1
#             elif category.name == "participation moyenne en classe":
#                 statistics.participation_moyenne += 1
#             elif category.name == "participation faible en classe":
#                 statistics.participation_faible += 1
#             elif category.name == "bonne moyenne aux tests/évaluations":
#                 statistics.bonne_moyenne += 1
#             elif category.name == "mauvaise moyenne aux tests/évaluations":
#                 statistics.mauvaise_moyenne += 1
#         statistics.save()
