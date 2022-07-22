from cProfile import label
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import markdown2
from . import util
from django.views import defaults
from django.urls import reverse
import re
from django import forms
import random



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request,title):
    markdowner = markdown2.Markdown()
    if util.get_entry(title):
        converted_text = markdowner.convert(util.get_entry(title))
    
        return render(request, "encyclopedia/entry.html",{
            "entry":converted_text,"title":title,
        }) 
    return HttpResponse(defaults.page_not_found(request, "exception", template_name='404.html'))


def search(request):
    
    query = request.GET.get('q')
    if util.get_entry(query):
        return HttpResponseRedirect(reverse('entry',args=[query]))
        
    else:
        entries = util.list_entries()
        possibilities = []
        string = re.compile("(?i)(" + query + ")")
        
        for entry in entries:
            if string.search(entry):
                possibilities.append(entry)

        return render(request, "encyclopedia/search.html", {
            'possibilities':possibilities, 'title':query,
        })
   


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title",widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(label="Content",widget=forms.Textarea(attrs={'class': 'form-control'}))



def new_page(request):
    
    if request.method == "POST":
        
        form = NewPageForm(request.POST)
        
        if form.is_valid():
            
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            entries = util.list_entries()
            
            if title in entries:
                return render(request, "encyclopedia/create.html",{
                    "error_message":"This entry already exists in the disk!!",
                })
            else:
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", args=[title]))
        

    return render(request, "encyclopedia/create.html",{
        "form":NewPageForm()
    })
    
 
 
class EditForm(forms.Form):
    
    new_content = forms.CharField(label="New Content",widget=forms.Textarea(attrs={'class': 'form-control'}))


def edit(request,title):
    
    populated_form = EditForm(initial={'new_content':util.get_entry(title)})
    
    if request.method == "POST":
        form = EditForm(request.POST)
        
        if form.is_valid():
            new_content = form.cleaned_data['new_content']
            util.save_entry(title,new_content)
            return HttpResponseRedirect(reverse("entry", args=[title]))
    
    return render(request, "encyclopedia/edit.html",{
        'form':populated_form,'title':title,
    })
    
    
def random_page(request):
    entries = util.list_entries()
    
    choice = random.choice(entries)
    
    return HttpResponseRedirect(reverse("entry", args=[choice]))

    