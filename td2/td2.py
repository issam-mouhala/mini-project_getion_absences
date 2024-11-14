
'-------------------exercise 1---------------'
'''
l=[1,4,8,2,5,7,9,10,10,7,6]
c=l[0]
new=[]
for i in range (len(l)) :
    for j in range(len(l)) :
        if l[j]<l[i] :
            c=l[i]
            l[i]=l[j]
            l[j]=c

for i in l :
    if l[0]!=i:
        new.append(i)
        
print("deuxieme max nombre est :",new[0])
'''
'-------------------exercise 2---------------'
'''
l=["issam","issam","mohammed","ali","mostafa","ali"]
n_dob=0
new=[]
for i in l :
    if(i in new) :
        n_dob+=1
    else :
        new.append(i)

print('nombre de doublons est : ',n_dob)
print(new)
'''
'-------------------exercise 3---------------'
'''
liste = list(range(1, 51))
new=[]
n=5
for i in range(0,50,n) :
 new.append(liste[i:i+n])
print(new)
'''
'-------------------exercise 4---------------'
'''
t1=(1,2,3)
t2=(4,5,6)
new=()
for i in range (len(t1)):
    new=new+(t1[i],)+(t2[i],)


print(new)
'''
'-------------------exercise 5---------------'
'''
l="issam is a goat a ostora a goat hhhhh m m "
new=[]
f=[]
desc={}
a=''
for i in l :
    if i==' ' or i=='\0' :
        new.append(a)
        a=''
    else :
        a=a+i
new.sort()
for i in new :
    f.append(new.count(i))
i=0
while(i<len(f)) :
    
    desc.update({new[i]:f[i]})
    i+=1

print(desc)
'''
'-------------------exercise 6---------------'
'''
desc={"issam":{
    'age':22,
    'notes':[1]
    },
    "rayan":{
    'age':19,
    'notes':[20,15]     
    },
    "moha":{
    'age':18,
    'notes':[10,18]     
    }}
moy=[]
for i in desc.keys():
    m=0
    for j in desc[i]["notes"]:
        m=m+j
    moy.append([i,m/len(desc[i]["notes"])])

j=0
for i in desc.keys():
        desc[i].update({"moy":moy[j][1]})
        j+=1
desc=dict(sorted(desc.items(), key=lambda item: item[1], reverse=True))
print(desc)
'''
'-------------------exercice 7---------------'
'''
desc={
    'taroudant':26,
    'agadir':21,
     'casablanca':20
}
def max_min_temp(desc):
  max=0
  min=0
  temp=[]
  for i in desc.values():
    temp.append(i)
  temp.sort() 
  print(temp) 


  max=temp[len(temp)-1]
  min=temp[0]
  for i in desc.keys():
      if desc[i]==max :
          max=i
      if desc[i]==min:
          min=i
  print("la ville avec la température la plus élevée:",max)
  print("la ville avec la température la plus basse :",min)

max_min_temp(desc)
'''
'-------------------exercice 8---------------'
'''
dect1 = {"issam": 25, "rayan": 30, "koyo": 35}
dect2 = {"badr": 28, "mehdi": 40, "walid": 32}

new_dect = dect1.copy() 

for key, value in dect2.items():
    if key in new_dect:
        new_dect[key] = max(new_dect[key], value)
    else:
        new_dect[key] = value

print("Dictionnaire combiné:", new_dect)
'''
'-------------------exercice 9---------------'
'''
desc={"bimo":50,"tide":15,"danone":41}
def filter(desc):
    for i in desc.keys():
        if desc[i]<50 :
           desc[i]=desc[i]*0.1+desc[i]

filter(desc)
print(desc)
'''
'-------------------exercice 10---------------'
'''
t=(('maroc',60),('usa',200),("egypt",100))
def convert(t):
    desc={}
    i=0
    for j in t:
        desc.update({t[i][0]:t[i][1]})
        i+=1
        desc=dict(sorted(desc.items(), key=lambda item: item[1], reverse=True))
    return desc
t=convert(t)
print(t)
'''