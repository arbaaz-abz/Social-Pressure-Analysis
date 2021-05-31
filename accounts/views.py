from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def signup(request):
    if request.method == "POST":
        if (
            request.POST["username"] == ""
            or request.POST["email"] == ""
            or request.POST["password"] == ""
            or request.POST["confirm_password"] == ""
        ):
            return render(
                request,
                "accounts/signup.html",
                {
                    "error": "Please complete all the fields!",
                    "username": request.POST["username"],
                    "email": request.POST["email"],
                },
            )
        if request.POST["password"] == request.POST["confirm_password"]:
            try:
                user = User.objects.get(username=request.POST["username"])
                return render(
                    request,
                    "accounts/signup.html",
                    {
                        "error": "This User already Exists, Please try a different username",
                        "email": request.POST["email"],
                    },
                )
            except User.DoesNotExist:
                User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password"],
                    email=request.POST["email"],
                )
                return render(request, "accounts/signup.html")
        else:
            return render(
                request,
                "accounts/signup.html",
                {
                    "error": "Pasword's did not match !!",
                    "username": request.POST["username"],
                    "email": request.POST["email"],
                },
            )
    else:
        return render(request, "accounts/signup.html")


def log_in(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if username == "" or password == "":
            return render(
                request,
                "accounts/login.html",
                {
                    "error": "Please complete all the fields!",
                    "username": request.POST["username"],
                },
            )
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page
            if request.POST["next"] != "":
                return redirect(request.POST["next"].rstrip("/"))
            else:
                return redirect("home")
        else:
            return render(
                request,
                "accounts/login.html",
                {"error": "Incorrect Username or Password"},
            )
    else:
        return render(request, "accounts/login.html")


def log_out(request):
    if request.method == "POST":
        logout(request)
        return redirect("index")
