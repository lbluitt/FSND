#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from functools import wraps


# In[ ]:


# Our Basic Function Defn
def print_name(name):
    print(name)
    
print_name("jimmy")


# In[ ]:


# Let's add a simple decorator to inject a greeting
def add_greeting(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print("Hello!")
        return f(*args, **kwargs)
    return wrapper

@add_greeting
def print_name(name):
    print(name)


print_name("sandy")


# In[ ]:


# Let's add some complexity in the form of a paramater
def add_greeting(greeting=''):
    def add_greeting_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(greeting)
            return f(*args, **kwargs)
        return wrapper
    return add_greeting_decorator

@add_greeting("what's up!")
def print_name(name):
    print(name)


print_name("kathy")


# In[ ]:


# We can also pass information back to the wrapped method
def add_greeting(greeting=''):
    def add_greeting_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(greeting)
            return f(greeting, *args, **kwargs)
        return wrapper
    return add_greeting_decorator

@add_greeting("Yo!")
def print_name(greeting, name):
    print(greeting)
    print(name)


print_name("Abe")

