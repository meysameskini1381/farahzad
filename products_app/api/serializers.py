from rest_framework import serializers
from products_app.models import *
from rest_framework.pagination import PageNumberPagination

# =========================
# Category
# =========================
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'slug',
            'parent',
            'is_main',
            'children',
        )

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data





# =========================
# Product List / Create
# =========================
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'slug',
            'price',
            'discount_price',
            'stock',
            'vip',
            'is_featured',
            'image',
            'short_description',
            'category',
            'category_id',
        )




# =========================
# Product Comment
# =========================
class ProductCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ProductComment
        fields = (
            'id',
            'text',
            'created_at',
            'replies',
            'email',
            'name',
        )

    def get_replies(self, obj):
        qs = obj.replies.filter(is_active=True).order_by('created_at')
        return ProductCommentSerializer(qs, many=True).data




class ProductCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ('text', 'parent', 'name', 'email')

    def validate(self, attrs):
        request = self.context['request']

        if not request.user.is_authenticated:
            if not attrs.get('name') or not attrs.get('email'):
                raise serializers.ValidationError(
                    "برای کاربران مهمان، نام و ایمیل الزامی است"
                )

        return attrs

    def validate_parent(self, parent):
        product = self.context['product']
        if parent and parent.product_id != product.id:
            raise serializers.ValidationError("reply نامعتبر است")
        return parent

    def create(self, validated_data):
        request = self.context['request']
        product = self.context['product']

        user = request.user if request.user.is_authenticated else None

        return ProductComment.objects.create(
            product=product,
            user=user,
            text=validated_data['text'],
            parent=validated_data.get('parent'),
            name=validated_data.get('name'),
            email=validated_data.get('email'),
        )




# =========================
# Product Gallery
# =========================
class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = (
            'image',
            'is_main',
        )


# =========================
# Product Feature
# =========================
class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = (
            'title',
            'value',
        )


# =========================
# Product Detail
# =========================
class ProductDetailSerializer(serializers.ModelSerializer):
    gallery = ProductGallerySerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'slug',
            'price',
            'discount_price',
            'description',
            'gallery',
            'features',
            'comments',
        )

    def get_comments(self, obj):
        # فرض بر این است که obj.product_comments همیشه موجود است (که هست)
        qs = obj.product_comments.filter(
            parent__isnull=True,
            is_active=True  # <--- آیا فیلد is_active در ProductComment وجود دارد؟ (بله، فرستادید)
        ).order_by('-created_at')  # <--- آیا فیلد created_at در ProductComment وجود دارد؟ (بله، فرستادید)

        return ProductCommentSerializer(qs, many=True).data


# =========================
# Pagination
# =========================
class ProductPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 100
