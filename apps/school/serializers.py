from rest_framework import serializers


from . models import SchoolYear, Classe, School, Student, Teacher, StudentStatistics


class SchoolYearSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = SchoolYear
        fields = ['id', 'start_date', 'end_date']

    def get_start_date(self, obj):
        return obj.start_date.year

    def get_end_date(self, obj):
        return obj.end_date.year


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'agent', 'address']

class ClasseSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    school_year = SchoolYearSerializer(read_only=True)

    class Meta:
        model = Classe
        fields = ['id', 'school', 'name', 'level', 'teacher', 'school_year']
    
    def get_teacher(self, obj):
        # Récupérez seulement des informations essentielles pour éviter la récursion.
        teacher = Teacher.objects.filter(classe=obj).first()
        if teacher:
            return {
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'phone': teacher.phone
            }
        return None

class TeacherSerializer(serializers.ModelSerializer):
    classe_infos = ClasseSerializer(read_only=True)
    school_year = SchoolYearSerializer(read_only=True)
    school_year_id = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all(), source='school_year', write_only=True)
    classe_id = serializers.PrimaryKeyRelatedField(queryset=Classe.objects.all(), source='classe', write_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'phone', 'classe_infos', 'school_year', 'school_year_id', 'classe_id']


class StudentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'image']

    def update(self, instance, validated_data):
        image = validated_data.get('image', instance.image)
        if image:
            instance.image = image
        instance.save()
        return instance

class StudentSerializer(serializers.ModelSerializer):
    classe_infos = ClasseSerializer(read_only=True)
    school_infos = serializers.SerializerMethodField()
    school_year = SchoolYearSerializer(read_only=True)
    school_year_id = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all(), source='school_year', write_only=True)
    classe_id = serializers.PrimaryKeyRelatedField(queryset=Classe.objects.all(), source='classe', write_only=True)

    class Meta:
        model = Student
        fields = ['id', 'matricule', 'first_name', 'last_name', 'date_of_birth', 'image', 'classe_infos', 'school_infos', 'school_year', 'school_year_id', 'classe_id']

    def get_school_infos(self, obj):
        return SchoolSerializer(obj.classe.school).data
