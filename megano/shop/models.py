from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название категории")
    image = models.ImageField(
        upload_to="categories/", null=True, blank=True, verbose_name="изображение"
    )

    def __str__(self):
        return self.title


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="subcategories",
        on_delete=models.CASCADE,
        default="",
        verbose_name="категория",
    )
    title = models.CharField(max_length=255, verbose_name="название подкатегории")
    image = models.ImageField(
        upload_to="subcategories/", null=True, blank=True, verbose_name="изображение"
    )

    def __str__(self):
        return self.title


class SalePrice(models.Model):
    """Модель для хранения информации о скидке на продукт"""

    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="цена со скидкой"
    )
    date_from = models.DateField(null=True, blank=True, verbose_name="дата начала")
    date_to = models.DateField(null=True, blank=True, verbose_name="дата окончания")


class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name="название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="цена")
    category = models.ForeignKey(
        Category,
        related_name="product",
        on_delete=models.CASCADE,
        verbose_name="категория",
    )
    description = models.TextField(max_length=1000, blank=True, verbose_name="описание")
    salePrice = models.ForeignKey(
        SalePrice,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="скидка на товар",
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    freeDelivery = models.BooleanField(default=True, verbose_name="бесплатная доставка")
    tags = models.ManyToManyField("Tag", related_name="tags", verbose_name="тэги")
    images = models.ManyToManyField("ProductImage", verbose_name="изображение")
    limited_edition = models.BooleanField(
        default=True, verbose_name="лимитированный продукт"
    )
    rating = models.FloatField(default=3.4, verbose_name="рейтинг")
    count = models.IntegerField(default=1, verbose_name="колличество")
    fullDescription = models.TextField(
        max_length=1000, blank=True, verbose_name="полное описание"
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.CharField(max_length=255, verbose_name="автор")
    email = models.EmailField(verbose_name="электронная почта")
    text = models.TextField(verbose_name="текст")
    rate = models.IntegerField(verbose_name="рейтинг")
    date = models.DateTimeField(auto_now_add=True, verbose_name="дата создания отзыва")
    product = models.ForeignKey(
        Product,
        related_name="reviews",
        on_delete=models.CASCADE,
        default="",
        null=True,
        verbose_name="товар",
    )

    def __str__(self):
        return self.author


class Specification(models.Model):
    name = models.CharField(max_length=50, default="", verbose_name="название")
    value = models.CharField(max_length=30, default="", verbose_name="значение")
    product = models.ForeignKey(
        Product,
        related_name="specifications",
        on_delete=models.CASCADE,
        verbose_name="товар",
    )


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name="название")

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    src = models.ImageField(
        upload_to="products/", null=True, blank=True, verbose_name="ссылка"
    )
    alt = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="описание"
    )
