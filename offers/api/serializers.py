from rest_framework import serializers
from offers.models import Package, Detail

#Serializer of a single detail from an Offer-Package.
#Is just sorting the properties.
class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

#For creating url to offer detail
class DetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='offers-detail'
    )

    class Meta:
        model = Detail
        fields = ['id', 'url']

#Serializer for Offer-Packages.
#Checks whether or not min_price and min_delivery_time are existing and if yes gets their value.
class PackageSerializer(serializers.ModelSerializer):
    details = DetailLinkSerializer(many=True, read_only=True)
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

#Serializer for validating the request body when posting a new Offer-Package.
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
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()
        if details_data is not None:
            instance.details.all().delete()
        for detail in details_data:
            Detail.objects.create(package=instance, **detail)
        return instance
    
#Serializer for creating the response body when posting a new Offer-Package.

class PackageCreateResponseSerializer(serializers.ModelSerializer):
    details= DetailSerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields= [
            'id',
            'title',
            'image',
            'description',
            'details'
        ]

#Serializer for creating a offer-detail.
class DetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = ['package', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


