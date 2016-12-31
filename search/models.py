# -*- coding: utf-8 -*-
from django.db import models
# from django.contrib.auth.models import AbstractUser

# # 用户模型.
# # 采用的继承方式扩展用户信息
# # 扩展：关联的方式去扩展用户信息
# class User(AbstractUser):
#     avatar = models.ImageField(upload_to='avatar/%Y/%m', default='avatar/default.png', max_length=200, blank=True, null=True, verbose_name='用户头像')
#     email = models.CharField(max_length=30, blank=True, null=True, unique=True, verbose_name='email')
#
#     class Meta:
#         verbose_name = '用户'
#         verbose_name_plural = verbose_name
#         ordering = ['-id']
#
#     def __str__(self):
#         return self.username
