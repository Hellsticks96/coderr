from rest_framework import serializers
from offers.models import Package, Detail

class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class PackageSerializer(serializers.ModelSerializer):
    details = DetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

    def get_min_price(self, obj):
        if obj.details.exists():
            return min([d.price for d in obj.details.all()])
        return None

    def get_min_delivery_time(self, obj):
        if obj.details.exists():
            return min([d.delivery_time_in_days for d in obj.details.all()])
        return None

class PackageCreateSerializer(serializers.ModelSerializer):
    details = DetailSerializer(many=True)

    class Meta:
        model = Package
        fields = ['title', 'image', 'description', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        package = Package.objects.create(**validated_data)
        for detail in details_data:
            Detail.objects.create(package=package, **detail)
        return package


class DetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = ['package', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
