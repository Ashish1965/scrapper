import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import io
from application import db
from datetime import datetime
import seaborn as sns
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt



def datacollect(url,page,index):
    url=url+str(1)
    if page==1:
        url=url[:-1]
        page=2
    response=requests.get(url)
    soup=BeautifulSoup(response.text,"lxml")
    print(url)

    title=[]
    trfirst=soup.find("tr")
    print(trfirst)
    thlist=trfirst.find_all("th")
    for i in thlist:
        title.append(remove(i.text.strip()))

    print('titles : ',title)
    df=pd.DataFrame(columns=title)


    for k in range(1,page):
        if(response.status_code!=200):
            break
        else:
            
            tr=soup.find_all("tr")

            for row in tr[1:]:
                tdlist=row.find_all("td")
                td=[remove(data.text.strip()) for data in tdlist]

                try:

                    length=len(df)
                    df.loc[length]=td

                except:
                    print("Mismatched columns",td)
    
    df.to_csv(f"application\datafiles\collectedData{index}.csv")
    return df,title




def calldata(name):
    filename=name.split(".")
    print(name)
    if name=="sampledata.csv":
        df=pd.read_csv(f"application\datafiles\{name}")
    
    elif( filename[-1]=="csv"):
        print(name[:9])
        if name[:9]=="collected":
            df=pd.read_csv(f"application\datafiles\{name}")
        else:
            df=pd.read_csv(f"application\datafiles\ {name}")

    elif filename[-1]=="xlsx":
        df=pd.read_excel(f"application\datafiles\ {name}")

    elif filename[-1]=="xls":
        df=pd.read_excel(f"application\datafiles\ {name}")
    
    

    title= [column for column in df.columns]
    print(len(df))
    return df,title



def remove(string):
    return "".join(string.split())

def pagination(number,last,df,no_of_post,filename):
    if(not str(number).isnumeric()):
         number=1

    number=int(number)

    df=df[(number-1)*int(no_of_post):(number-1)*int(no_of_post)+int(no_of_post)]

    if(number==1):
        prev="#"
        next=f"/collectedData?filename={filename}&number={number+1}"

    elif(number==last): 
        prev="#"
        next=f"/collectedData?filename={filename}&number={number-1}" 
     
    else:
        prev=f"/collectedData?filename={filename}&number={number-1}"
        next=f"/collectedData?filename={filename}&number={number+1}"
        
    return df,number,prev,next



def numerical_col(df):
    numerical_cols=[]
    for column in df.columns:
        if (df[column].dtypes!="object"):
            numerical_cols.append(column)
    return numerical_cols

def object_col(df):
    object_cols=[]
    for column in df.columns:
        if (df[column].dtypes=="object"):
            object_cols.append(column)
    return object_cols

def correlation(df):
    numerical_cols=numerical_col(df)
    new_df=df[numerical_cols]
    new_df=new_df.corr()
    title=new_df.columns
    return new_df,title


def pairplots(new_df):
    sns.pairplot(new_df)
    plt.savefig("application/static/img/plot.png")
    sns.pairplot(new_df,kind="kde")
    plt.savefig("application/static/img/kde.png")
    sns.pairplot(new_df,kind="reg")
    plt.savefig("application/static/img/Reg.png")
    sns.pairplot(new_df,kind="hist")
    plt.savefig("application/static/img/hist.png")

    
def graphs(graph,x,y,hue,df):
   
    if graph=="Lineplot":
        if hue!="None":
            sns.lineplot(x=x,y=y,data=df,hue=hue)

        else:
            sns.lineplot(x=x,y=y,data=df)


    elif graph=="Scatterplot":
        if hue!="None":
            sns.scatterplot(x=x,y=y,data=df,hue=hue)
        else:
            sns.scatterplot(x=x,y=y,data=df)


    elif graph=="Barplot":
        if hue!="None":
            sns.barplot(x=x,y=y,data=df,hue=hue,ci=10 ,alpha=0.9)
        else:
            sns.barplot(x=x,y=y,data=df,ci=10 ,alpha=0.9)

    elif graph=="Boxplot":
        if hue!="None":
            sns.boxplot(x=x,y=y, data=df,hue=hue)
        else:
            sns.boxplot(x=x,y=y, data=df)
        

    elif graph=="Heatmap":
        cor_data,cor_title=correlation(df)
        sns.heatmap(cor_data, cmap='RdBu_r',annot=True)

    elif graph=="Pairplot":
        if hue!="None":
            sns.pairplot(df,hue=hue)
        else:
            sns.pairplot(df)

    elif graph=="relplot":
        if hue!="None":
            sns.relplot(data=df,x=x, y=y,hue=hue)
        else:
            sns.relplot(data=df,x=x, y=y)

    elif graph=="lmplot":
        if hue!="None":
            sns.lmplot(data=df, x=x, y=y, hue=hue)
        else:
            sns.lmplot(data=df, x=x, y=y)

    elif graph=="jointplot":
        if hue!="None":
            sns.jointplot(data=df, x=x, y=y, hue=hue)
        else:
            sns.jointplot(data=df, x=x, y=y)

    elif graph=="violenplot":
        if hue!="None":
            sns.violinplot(x=x,y=y,data=df,hue=hue)
        else:
            sns.violinplot(data=df, x=x, y=y)

    elif graph=="Displot":
        if hue!="None":
            if x=="None":
                sns.displot(df[y],kde=True,color='green',hue=hue)
            else:
                sns.displot(df[x],kde=True,color='green',hue=hue)

        else:
            if x=="None":
                sns.displot(df[y],kde=True,color='green')
            else:
                sns.displot(df[x],kde=True,color='green')

    elif graph=="Countplot":
        if hue!="None":
            if x=="None":
                sns.countplot(x=y,data=df,hue=hue,alpha=1)
            else:
                sns.countplot(x=x,data=df,hue=hue,alpha=1)

        else:
            if x=="None":
                sns.countplot(x=y,data=df,alpha=1)
            else:
                sns.countplot(x=x,data=df,alpha=1)

    plt.savefig("application/static/img/graphs.png")
    plt.clf()
    



    





    
       

