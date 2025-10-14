from rest_framework import serializers
from orders.models import Order
from offers.models import Detail


class OrderSerializer(serializers.ModelSerializer):
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['offer_detail_id']

    def create(self, validated_data):
        request = self.context['request']
        customer_user = request.user
        detail_id = validated_data['offer_detail_id']

        detail = Detail.objects.select_related('package', 'package__user').get(id=detail_id)
        business_user = detail.package.user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            detail=detail,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
        )

        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
    
class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'created_at',
            'updated_at',
        ]
