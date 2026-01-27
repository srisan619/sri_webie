from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Document
from .forms import DocumentForm
from users.views import is_admin, is_auditor

@login_required
def document_list(request):
    documents = Document.objects.all()
    return render(request, "documents/document_list.html", {"documents": documents})

@login_required
def document_upload(request):
    if is_auditor(request.user):
        return HttpResponseForbidden("Read-only access")
    
    form = DocumentForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        doc = form.save(commit=False)
        doc.uploaded_by = request.user
        doc.save()
        messages.success(request, "Document uploaded successfully.")
        return redirect("document_list")
    
    return render(request, "documents/document_upload.html", {"form": form})
