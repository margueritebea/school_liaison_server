from django.db import models

# Create your models here.



# Category Notification Model 
class CategoryNotification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "6. Category Notification"

# Notification Model 
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sender")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student")
    categories = models.ManyToManyField(CategoryNotification, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    date = models.DateField()
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} | {self.student} {self.message}"

    def create_user_notifications(self):
        parents = self.student.profile_set.filter(user__role='parent')
        # for parent_profile in parents:
        #     # Récupérer la dernière souscription
        #     last_subscription = parent_profile.user.subscription_set.filter(student=self.student).order_by('-end_date').first()
        #     # Vérifier si la dernière souscription est active
        #     if last_subscription and last_subscription.status:
        #         UserNotification.objects.create(
        #             user=parent_profile.user,
        #             notification=self,
        #             student=self.student,
        #         )
        for parent_profile in parents:
            # Vérifier si la dernière souscription est active
            UserNotification.objects.create(
                user=parent_profile.user,
                notification=self,
                student=self.student,
            )

    @property
    def sender_profile(self):
        sender_profile = Profile.objects.get(user=self.sender)
        return sender_profile

    @property
    def student_infos(self):
        student_infos = self.student
        return student_infos

    @property
    def category_infos(self):
        category_infos = self.categories.all()
        return category_infos

    class Meta:
        verbose_name_plural = "7. Notification"

# User Notification Model 
class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.student}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "7.1 User Notification"
        unique_together = ('user', 'notification', 'student')    
