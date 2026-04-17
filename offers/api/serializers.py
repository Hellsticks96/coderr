from rest_framework import serializers

from offers.models import Detail, Package


class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class DetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="offers-detail")

    class Meta:
        model = Detail
        fields = ["id", "url"]


class PackageSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offer packages.

    Includes linked detail resources and computed fields for
    minimum price and delivery time.
    """

    details = DetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_min_price(self, obj):
        """
        Returns the lowest price among all related details.

        Args:
            obj (Package): The package instance.

        Returns:
            float | None: Minimum price or None if no details exist.
        """
        if obj.details.exists():
            return min(d.price for d in obj.details.all())
        return None

    def get_min_delivery_time(self, obj):
        """
        Returns the shortest delivery time among all related details.

        Args:
            obj (Package): The package instance.

        Returns:
            int | None: Minimum delivery time or None if no details exist.
        """
        if obj.details.exists():
            return min(d.delivery_time_in_days for d in obj.details.all())
        return None


class PackageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating offer packages.

    Handles nested creation and replacement of related detail objects.
    """

    details = DetailSerializer(many=True)

    class Meta:
        model = Package
        fields = ["title", "image", "description", "details"]

    def create(self, validated_data):
        """
        Creates a package along with its related details.

        Args:
            validated_data (dict): Validated input data.

        Returns:
            Package: The created package instance.
        """
        details_data = validated_data.pop("details", [])
        package = Package.objects.create(**validated_data)

        for detail in details_data:
            Detail.objects.create(package=package, **detail)

        return package

    def update(self, instance, validated_data):
        """
        Updates a package and replaces its related details.

        Args:
            instance (Package): The package instance to update.
            validated_data (dict): Validated input data.

        Returns:
            Package: The updated package instance.
        """
        details_data = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            instance.details.all().delete()
            for detail in details_data:
                Detail.objects.create(package=instance, **detail)

        return instance

    def validate(self, data):
        """
        Validates that each detail contains all required fields.

        Args:
            data (dict): Incoming request data.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If required fields are missing.
        """
        details = data.get("details")

        if details is not None:
            required_fields = [
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
            ]

            for detail in details:
                for field in required_fields:
                    if field not in detail:
                        raise serializers.ValidationError(
                            {"details": f"Field '{field}' is required for each detail."}
                        )

        return data


class PackageCreateResponseSerializer(serializers.ModelSerializer):
    details = DetailSerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = ["id", "title", "image", "description", "details"]


class DetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = [
            "package",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
