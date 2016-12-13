from rest_framework import serializers

class AuthUserSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)

    # Therapist or patient..
    type = serializers.IntegerField(read_only=True)

    username = serializers.CharField(read_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()

    email = serializers.EmailField(required=False)

    sex = serializers.IntegerField()
    fiscal_code = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    date_joined = serializers.DateTimeField(read_only=True)
    language = serializers.CharField()

    address_type_1 = serializers.IntegerField()
    address_1 = serializers.CharField(required=False)
    address_type_2 = serializers.IntegerField()
    address_2 = serializers.CharField(required=False)

    phone_type_1 = serializers.IntegerField()
    phone_1 = serializers.CharField(required=False)

    phone_type_2 = serializers.IntegerField()
    phone_2 = serializers.CharField(required=False)

    has_powers = serializers.BooleanField(read_only=True)

    pass
