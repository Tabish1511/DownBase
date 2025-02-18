from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, UploadFileForm
from .models import UserImage
from django.contrib.auth.decorators import login_required
from .utils import list_s3_images, upload_file_to_s3, delete_file_from_s3
from downBase.settings import CLOUDFRONT_URL

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('home')  # Redirect to a success page
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a success page
        else:
            # Return an error message
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to the homepage or login page



@login_required
def home(request):
    if request.method == 'POST':
        if 'file' in request.FILES:  # Handle file upload
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                # Upload file to S3 with user-specific path
                user_prefix = f"user_{request.user.id}/"
                file_name = user_prefix + file.name
                upload_file_to_s3(file, file_name)

                # Save metadata to the database
                UserImage.objects.create(user=request.user, file_name=file_name)
                return redirect('home')
        elif 'delete_file' in request.POST:  # Handle file deletion
            file_url = request.POST.get('delete_file')

            user_prefix = f"user_{request.user.id}/"
            file_name = file_url.split('/')[-1]
            user_file_name = user_prefix + file_name

            delete_file_from_s3(user_file_name)

            UserImage.objects.filter(user=request.user, file_name=user_file_name).delete()
            return redirect('home')
    else:
        form = UploadFileForm()

    # List images for the current user
    user_images = UserImage.objects.filter(user=request.user)
    cloudfront_url = CLOUDFRONT_URL
    image_urls = [f"{cloudfront_url}/{image.file_name}" for image in user_images]
    return render(request, 'home.html', {'user': request.user, 'image_urls': image_urls, 'form': form})
