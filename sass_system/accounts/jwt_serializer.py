from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom fields inside JWT token
        token["username"] = user.username
        token["role"] = user.role
        token["company"] = user.company_id if user.company else None

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data in login response
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "role": self.user.role,
            "company": self.user.company_id if self.user.company else None
        }

        return data