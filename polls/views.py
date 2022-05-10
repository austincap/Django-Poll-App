from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from .models import Poll, Choice, Vote, MiningNode
from .forms import PollAddForm, EditPollForm, ChoiceAddForm
from django.http import HttpResponse
# For timestamp
import datetime
# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib
# To store data
# in our blockchain
import json
import uuid
import base64
import sys
import time
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.signing import Signer
from os.path import exists
import numpy as np
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required()
def polls_list(request):
    all_polls = Poll.objects.all()
    search_term = ''
    if 'name' in request.GET:
        all_polls = all_polls.order_by('text')

    if 'date' in request.GET:
        all_polls = all_polls.order_by('pub_date')

    if 'vote' in request.GET:
        all_polls = all_polls.annotate(Count('vote')).order_by('vote__count')

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_polls = all_polls.filter(text__icontains=search_term)

    paginator = Paginator(all_polls, 6)  # Show 6 contacts per page
    page = request.GET.get('page')
    polls = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
    print(params)
    context = {
        'polls': polls,
        'params': params,
        'search_term': search_term,
    }
    return render(request, 'polls/polls_list.html', context)


@login_required()
def list_by_user(request):
    all_polls = Poll.objects.filter(owner=request.user)
    paginator = Paginator(all_polls, 7)  # Show 7 contacts per page

    page = request.GET.get('page')
    polls = paginator.get_page(page)

    context = {
        'polls': polls,
    }
    return render(request, 'polls/polls_list.html', context)


@login_required()
def polls_add(request):
    if request.user.has_perm('polls.add_poll'):
        if request.method == 'POST':
            form = PollAddForm(request.POST)
            if form.is_valid:
                poll = form.save(commit=False)
                poll.owner = request.user
                poll.save()
                new_choice1 = Choice(
                    poll=poll, choice_text=form.cleaned_data['choice1']).save()
                new_choice2 = Choice(
                    poll=poll, choice_text=form.cleaned_data['choice2']).save()

                messages.success(
                    request, "Poll & Choices added successfully.", extra_tags='alert alert-success alert-dismissible fade show')

                return redirect('polls:list')
        else:
            form = PollAddForm()
        context = {
            'form': form,
        }
        return render(request, 'polls/add_poll.html', context)
    else:
        return HttpResponse("Sorry but you don't have permission to do that!")


@login_required
def polls_edit(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid:
            form.save()
            messages.success(request, "Poll Updated successfully.",
                             extra_tags='alert alert-success alert-dismissible fade show')
            return redirect("polls:list")

    else:
        form = EditPollForm(instance=poll)

    return render(request, "polls/poll_edit.html", {'form': form, 'poll': poll})


@login_required
def polls_delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')
    poll.delete()
    messages.success(request, "Poll Deleted successfully.",
                     extra_tags='alert alert-success alert-dismissible fade show')
    return redirect("polls:list")


@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully.", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll.id)
    else:
        form = ChoiceAddForm()
    context = {
        'form': form,
    }
    return render(request, 'polls/add_choice.html', context)


@login_required
def choice_edit(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST, instance=choice)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice Updated successfully.", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll.id)
    else:
        form = ChoiceAddForm(instance=choice)
    context = {
        'form': form,
        'edit_choice': True,
        'choice': choice,
    }
    return render(request, 'polls/add_choice.html', context)


@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')
    choice.delete()
    messages.success(
        request, "Choice Deleted successfully.", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('polls:edit', poll.id)


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.active:
        return render(request, 'polls/poll_result.html', {'poll': poll})
    loop_count = poll.choice_set.count()
    context = {
        'poll': poll,
        'loop_time': range(0, loop_count),
    }
    return render(request, 'polls/poll_detail.html', context)


@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice')
    if not poll.user_can_vote(request.user):
        messages.error(
            request, "You already voted this poll!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:list")

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        vote = Vote(user=request.user, poll=poll, choice=choice)
        vote.save()
        print(vote)
        return render(request, 'polls/poll_result.html', {'poll': poll})
    else:
        messages.error(
            request, "No choice selected!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:detail", poll_id)
    return render(request, 'polls/poll_result.html', {'poll': poll})


@login_required
def endpoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if poll.active is True:
        poll.active = False
        poll.save()
        return render(request, 'polls/poll_result.html', {'poll': poll})
    else:
        return render(request, 'polls/poll_result.html', {'poll': poll})




def initializeNode(request):
    #check if blockdata exists on drive already
    # Create the object of the class blockchain
    #blockchain = Blockchain()
    miningnode = MiningNode()
    time = str(datetime.datetime.now())
    #create initial block
    block_height = 0
    prev_hash="000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
    prev_proof = 1 #aka nonce
    #check for existing blocks on drive
    done_processing_blocks = False
    data_from_datfile = {}
    print("begin processing blockdata")
    while(not done_processing_blocks):
        file = "block"+str(block_height)+".dat"
        #if existing file
        if(exists(file)):
            print("file exists")
            if(block_height==0):
                #miningnode.chain.append()
                with open(file) as datfile:
                    data_from_datfile = json.loads(datfile)
                    print("data from datfile")
                    print(str(file))
                    print(data_from_datfile)
                    print(base64.b64decode(data_from_datfile))
                    miningnode.previousBlock = base64.b64decode(data_from_datfile)
                print("genesis block data cant be verified until additional blocks are produced")
            else:
                with open(file) as datfile:
                    data_from_datfile = json.loads(datfile)
                    print("data from datfile")
                    print(str(file))
                    print(data_from_datfile)
                    print(base64.b64decode(data_from_datfile))
                    extractedBlockHeader = {"version":1, "proof":1, "prev_block_height":1, "prev_block_hash":"000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", "this_block_hash":"000000000099d934ff763ae46a2a6c1726689c085ae165831eb3f1b60a8ce26f", "time": 1651964655.709359}
                    extractedBlockTransactions = {"transactions":"data"}
                    #if merklerooted transactions of previous block = previous block's hash
                    if(miningnode.verifyBlock(miningnode.previousBlock["transactions"], extractedBlockHeader["prev_block_hash"])):
                        print("previous blocks merkle root hash is equal to this blocks prev_block_hash")
                        print("on to the next block")
                    else:
                        print("BAD BLOCKCHAIN!")
                        break
            block_height+=1
        else:
            if(block_height==0):
                #if no existing blocks, create first block
                # nodeversion, proof, prev_block_height, prev_hash
                #miningnode.createBlock(miningnode.miningnodeversion, 1, initial_block_height, initial_prev_hash)
                #automatically create first citizen so there is at least 1 transaction, genesis block hash same as vouching user id
                miningnode.createNewCitizen("00000000", {"name":"admin", "age":33})
                miningnode.createBasicIncome(miningnode.tempUser, {"points":100.0})
                #automatically create candidate block so there is something there 
                print("CREATE CANDIDASTE BLOCK")
                miningnode.createCandidateBlock(block_height, prev_proof, prev_hash)
            done_processing_blocks = True
    miningnode.latestBlockHeight = block_height
    return render(request, 'polls/poll_detail.html', {"data":"test"})
