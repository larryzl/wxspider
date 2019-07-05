#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 5:00 PM
@Author  : Larry
@Site    : 
@File    : account.py
@Software: PyCharm
@Desc    :

"""
import re
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.forms import widgets
from web_admin.models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField


# from web_admin.models import CustomUser


def email_check(email):
	pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
	return re.match(pattern, email)


class UserLoginForm(AuthenticationForm):
	username = forms.CharField(label='用户名', max_length=100,
	                            widget=widgets.Input(attrs={'class': "form-control"})
	                            )
	password = forms.CharField(
			label='密码', widget=forms.PasswordInput(attrs={'class': "form-control"}),
			max_length=128, strip=False,
	)

	# def clean_email(self):
	# 	email = self.cleaned_data.get('email')
	# 	if email_check(email):
	# 		filter_result = CustomUser.object.filter(email=email)
	# 		if len(filter_result) == 0:
	# 			raise forms.ValidationError("Your email not exists.")
	# 	else:
	# 		raise forms.ValidationError("Please enter a valid email.")
	# 	return email

	class Meta:
		model = CustomUser
		fields = ['username', 'password']

	# def confirm_login_allowed(self, user):
	# 	pass


class UserRegisterForm(forms.ModelForm):
	password1 = forms.CharField(
			label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}),
			max_length=128, strip=False, required=False,
	)
	password2 = forms.CharField(
			label='确认密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}),
			max_length=128, strip=False, required=False,
	)

	class Meta:
		model = CustomUser
		fields = ['username', 'nickname', 'email']
		widgets = {
			'nickname': forms.TextInput(attrs={'class': 'form-control'}),
			'username': forms.TextInput(attrs={'class': 'form-control'}),
			'email': forms.TextInput(attrs={'class': 'form-control'}),
		}

	def save(self, commit=True):
		print('save')
		password = self.cleaned_data.get('password1')
		user = super(UserRegisterForm, self).save(commit=False)
		user.set_password(password)
		if commit:
			user.save()
		return user

	def clean_username(self):
		username = self.cleaned_data.get('username')
		print("clean_username:", username)
		if len(username) < 6:
			raise forms.ValidationError("Your username must be at least 6 characters long.")
		elif len(username) > 50:
			raise forms.ValidationError("Your username is too long.")
		else:
			filter_result = CustomUser.object.filter(username=username)
		if len(filter_result) > 0:
			raise forms.ValidationError("Your username already exists.")
		return username

	def clean_email(self):
		email = self.cleaned_data.get('email')

		if email_check(email):
			filter_result = CustomUser.object.filter(email=email)
			if len(filter_result) > 0:
				raise forms.ValidationError("Your email already exists.")
		else:
			raise forms.ValidationError("Please enter a valid email.")
		return email

	def clean_password1(self):
		password1 = self.cleaned_data.get('password1')

		if len(password1) < 6:
			raise forms.ValidationError("Your password is too short.")
		elif len(password1) > 20:
			raise forms.ValidationError("Your password is too long.")

		return password1

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')

		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Password mismatch. Please enter again.")

		return password2

	@property
	def username(self):
		print(self.cleaned_data)
		username = self.cleaned_data.get('username')
		print('get username:', username)
		return username


class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = CustomUser
		fields = ('email', 'username', 'password', 'is_active', 'is_admin')

	def clean_password(self):
		return self.initial['password']
