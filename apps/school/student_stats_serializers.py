from rest_framework import serializers
from .models import Student, StudentStatistics

class StudentPerformanceSerializer(serializers.ModelSerializer):
    statistics = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    performance_score = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'matricule', 'image', 
            'statistics', 'class_info', 'performance_score'
        ]

    def get_statistics(self, obj):
        school_year = self.context.get('school_year')
        if school_year:
            stats = StudentStatistics.objects.filter(
                student=obj, 
                school_year=school_year
            ).first()
            if stats:
                return {
                    'absence': stats.absence,
                    'absence_autorisee': stats.absence_autorisee,
                    'mauvaise_conduite': stats.mauvaise_conduite,
                    'participation_moyenne': stats.participation_moyenne,
                    'participation_faible': stats.participation_faible,
                    'mauvaise_moyenne': stats.mauvaise_moyenne,

                    'presence': stats.presence,
                    'bonne_conduite': stats.bonne_conduite,
                    'participation_active': stats.participation_active,
                    'bonne_moyenne': stats.bonne_moyenne
                }
        return {}

    def get_class_info(self, obj):
        return {
            'class_name': obj.classe.name if obj.classe else None,
            'level': obj.classe.level if obj.classe else None,
            'school_name': obj.classe.school.name if obj.classe and obj.classe.school else None
        }

    def get_performance_score(self, obj):
        stats = self.get_statistics(obj)
        if stats:
            return (
                stats['presence'] * 0.2 +
                stats['bonne_conduite'] * 0.3 +
                stats['participation_active'] * 0.3 +
                stats['bonne_moyenne'] * 0.2
            )
        return 0


class SchoolClassPerformanceSerializer(serializers.Serializer):
    school_name = serializers.CharField(source='school.name')
    class_name = serializers.CharField(source='classe.name')
    class_level = serializers.CharField(source='classe.level')
    school_year = serializers.SerializerMethodField()
    
    # Totaux de chaque action
    total_students = serializers.IntegerField(source='stats.total_students')
    total_absence = serializers.IntegerField(source='stats.total_absence')
    total_absence_autorisee = serializers.IntegerField(source='stats.total_absence_autorisee')
    total_presence = serializers.IntegerField(source='stats.total_presence')
    total_mauvaise_conduite = serializers.IntegerField(source='stats.total_mauvaise_conduite')
    total_bonne_conduite = serializers.IntegerField(source='stats.total_bonne_conduite')
    total_participation_active = serializers.IntegerField(source='stats.total_participation_active')
    total_participation_moyenne = serializers.IntegerField(source='stats.total_participation_moyenne')
    total_participation_faible = serializers.IntegerField(source='stats.total_participation_faible')
    total_bonne_moyenne = serializers.IntegerField(source='stats.total_bonne_moyenne')
    total_mauvaise_moyenne = serializers.IntegerField(source='stats.total_mauvaise_moyenne')
    
    # Score de performance
    performance_score = serializers.SerializerMethodField()

    def get_school_year(self, obj):
        return f"{obj['school_year'].start_date.year}-{obj['school_year'].end_date.year}"

    def get_performance_score(self, obj):
        return (
            obj['stats']['total_presence'] * 0.2 +
            obj['stats']['total_bonne_conduite'] * 0.3 +
            obj['stats']['total_participation_active'] * 0.3 +
            obj['stats']['total_bonne_moyenne'] * 0.2
        )
    

class SchoolLevelPerformanceSerializer(serializers.Serializer):
    school_name = serializers.CharField(source='school.name')
    level = serializers.CharField()
    school_year = serializers.SerializerMethodField()
    class_count = serializers.IntegerField()
    student_count = serializers.IntegerField()
    
    # Totaux de chaque action
    total_absence = serializers.IntegerField(source='stats.total_absence')
    total_absence_autorisee = serializers.IntegerField(source='stats.total_absence_autorisee')
    total_presence = serializers.IntegerField(source='stats.total_presence')
    total_mauvaise_conduite = serializers.IntegerField(source='stats.total_mauvaise_conduite')
    total_bonne_conduite = serializers.IntegerField(source='stats.total_bonne_conduite')
    total_participation_active = serializers.IntegerField(source='stats.total_participation_active')
    total_participation_moyenne = serializers.IntegerField(source='stats.total_participation_moyenne')
    total_participation_faible = serializers.IntegerField(source='stats.total_participation_faible')
    total_bonne_moyenne = serializers.IntegerField(source='stats.total_bonne_moyenne')
    total_mauvaise_moyenne = serializers.IntegerField(source='stats.total_mauvaise_moyenne')
    
    # Score de performance
    performance_score = serializers.SerializerMethodField()

    def get_school_year(self, obj):
        return f"{obj['school_year'].start_date.year}-{obj['school_year'].end_date.year}"

    def get_performance_score(self, obj):
        return (
            obj['stats']['total_presence'] * 0.2 +
            obj['stats']['total_bonne_conduite'] * 0.3 +
            obj['stats']['total_participation_active'] * 0.3 +
            obj['stats']['total_bonne_moyenne'] * 0.2
        )


class SchoolPerformanceSerializer(serializers.Serializer):
    school_name = serializers.CharField(source='school.name')
    school_year = serializers.SerializerMethodField()
    class_count = serializers.IntegerField()
    student_count = serializers.IntegerField()
    
    # Totaux de chaque action
    total_absence = serializers.IntegerField(source='stats.total_absence')
    total_absence_autorisee = serializers.IntegerField(source='stats.total_absence_autorisee')
    total_presence = serializers.IntegerField(source='stats.total_presence')
    total_mauvaise_conduite = serializers.IntegerField(source='stats.total_mauvaise_conduite')
    total_bonne_conduite = serializers.IntegerField(source='stats.total_bonne_conduite')
    total_participation_active = serializers.IntegerField(source='stats.total_participation_active')
    total_participation_moyenne = serializers.IntegerField(source='stats.total_participation_moyenne')
    total_participation_faible = serializers.IntegerField(source='stats.total_participation_faible')
    total_bonne_moyenne = serializers.IntegerField(source='stats.total_bonne_moyenne')
    total_mauvaise_moyenne = serializers.IntegerField(source='stats.total_mauvaise_moyenne')
    
    # Score de performance (calculé à partir des totaux des indicateurs positifs)
    performance_score = serializers.SerializerMethodField()

    def get_school_year(self, obj):
        return f"{obj['school_year'].start_date.year}-{obj['school_year'].end_date.year}"

    def get_performance_score(self, obj):
        return (
            obj['stats']['total_presence'] * 0.2 +
            obj['stats']['total_bonne_conduite'] * 0.3 +
            obj['stats']['total_participation_active'] * 0.3 +
            obj['stats']['total_bonne_moyenne'] * 0.2
        )
    
    
