from flask import*
import math
import bcrypt
from datetime import datetime
from application import app
from .form import ContactForm,authForm
from application import db
from .modules import calldata,datacollect,pagination,correlation,pairplots,numerical_col,object_col,graphs
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt





@app.route("/Signup",methods=["POST","GET"])
def signup():
    if request.method == "POST":
        form = authForm(request.form)
        username = form.uname.data
        email = form.email.data
        password = form.password.data
        passw=password.encode('utf-8')
        salt = bcrypt.gensalt(10)
        hash = bcrypt.hashpw(passw, salt)

        user=db.User.find_one({"email":email})
        if not user: 
            db.User.insert_one({
                "Username": username,
                "email":email,
                "password":hash,
                "Date": datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
            })
            flash(f"{username} is successfully Signed up", "success")
            return redirect("/login")
        
        else:
            flash(f"{user} with this {email} is already exits.","error")
            return redirect(url_for("signup"))


    else:
        form =authForm()
    return render_template('signup.html',form = form,link="Already Have a Account ?",title="SignUp")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        form = authForm(request.form)
        email = form.email.data
        username=form.uname.data
        password = form.password.data
        passw=password.encode('utf-8')

        user=db.User.find_one({"email":email})
        if not user:
            flash(f"404 {username} Not Found", "error")
            return "<h1> 404 User Not Found </h1>"
        else:
    
            user_password=user['password']
            result = bcrypt.checkpw(passw, user_password)
            if username==user["Username"] and result:
                session["logged_in"]=True
                session["id"]=str(user["_id"])
                session["user"]=user["Username"]
                session["email"]=user["email"]
                session["filename"]="sampledata.csv"

                db.Sessions.insert_one(
                    {
                        "email":session["email"],
                        "id":session["id"],
                        "files":[{
                            "filename":session["filename"],
                            "Date":datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
                        }]


                    }
                )
                flash(f"{username} is successfully Logged in!","success")
                return redirect("/")
            
            flash("Invalid Credentials ! ","warning")
            return redirect(url_for("login")) 
        
    form =authForm()
    return render_template("login.html",form=form,link="Don't Have Account ?",title="SignUp")



@app.route("/")
def home():
        if "logged_in" in session and session['logged_in']==True:
            zip=True
        else:
            zip=False
        data,title=calldata('sampledata.csv')
        return render_template('home.html',data="Sample Data",collection=data,keys=title,zip=zip)
   


@app.route('/collectedData',methods=['GET','POST'])

def collectedData():
    if "logged_in" in session and session['logged_in']==True:
        zip=True
        if(request.method=='POST'):
            url=request.form['url']
            page=request.form['page']
            f=request.files['file']
            if len(request.form['url'])!=0:
                page=int(page)
                session_data=db.Sessions.find_one({"email":session["email"]})
                filename="collectedData"+str(len(session_data["files"]))+".csv"
                data,title=datacollect(url,page,str(len(session_data["files"])))
                document={
                    "filename":filename,
                    "url":url,
                    "Date":datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
                }
                session_data['files'].append(document)
                db.Sessions.find_one_and_update({"email":session["email"]},{"$set":{"files":session_data["files"]}})
                

            else:
                session_data=db.Sessions.find_one({"email":session["email"]})
                f.save("application\datafiles\ "+f.filename)
                filename=f.filename
                session["filename"]=filename
                document={
                    "filename":filename,
                    "Date":datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
                }
                session_data['files'].append(document)
                db.Sessions.find_one_and_update({"email":session["email"]},{"$set":{"files":session_data["files"]}})
                flash("Dataset is loaded Successfully , Now You are able to Analysis Your Data File in the Feature Section of Services tab","info")
            return redirect(url_for('collectedData', filename=filename)) 
        
        if(request.method=='GET'):
            filename = request.args['filename']
            number=request.args.get('number')
            df,title=calldata(filename)
            no_of_post=20
            last=math.ceil(len(df)/int(no_of_post))
            data,number,prev,next=pagination(number,last,df,no_of_post,filename)
            dict={"collection":data,
                "keys":title,
                "data":"Collected Data",
                "number":number,
                "prev":prev,
                "next":next,
                "post":no_of_post,
                "filname":filename
                }
            print(data)
            print('prev',prev)
            print('next',next)
            print('number',number)
            
            return render_template('collectedData.html',dict=dict,zip=zip)
    else:
        zip=False
        return redirect("/login")
        

        
@app.route("/Service")
def service():
    if "logged_in" in session and session['logged_in']==True:
        zip=True
        return render_template('service.html',zip=zip)
    else:
        zip=False
    return redirect("/login")

    

@app.route("/About")
def about():
    if "logged_in" in session and session['logged_in']==True:
        zip=True
    else:
        zip=False
    return render_template('about.html',zip=zip)



@app.route("/Contact",methods=["POST","GET"])
def contact():
    if "logged_in" in session and session['logged_in']==True:
        zip=True
    else:
        zip=False
    if request.method == "POST":
        form = ContactForm(request.form)
        name = form.name.data
        email = form.email.data
        message = form.message.data
        suggestion=form.suggestion.data

        db.contacts.insert_one({
            "name": name,
            "email":email,
            "message": message,
            "suggestion":suggestion,
            "Date": datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
        })
        flash(f"Contact details of {name} is successfully added", "success")
        return redirect("/Contact")
    else:
        form = ContactForm()
    return render_template('contact.html',form = form,zip=zip)


@app.route("/FeatureAnalysis")
def feature():

    if "logged_in" in session and session['logged_in']==True:
        zip=True
        image="abc"
        print(image)
        sess=db.Sessions.find_one({"email":session["email"]})
        filename=sess["files"][len(sess["files"])-1]["filename"]
        if filename:
            df,title=calldata(filename)
            statis_data=df.describe()
        else:
            df,title=calldata("sampledata.csv")
            statis_data=df.describe()
            statis_data.drop('Unnamed: 0',inplace=True,axis=1)

        pairplots(df)
        title=statis_data.columns
        title.insert(0,"feature")
        print(title)
        index=statis_data.index

        cor_data,cor_title=correlation(df)
        len_corr=len(cor_data)
        print(cor_data)

        return render_template('feature.html',image=image,data=statis_data,column=title,length=len(statis_data),idx=index,corr=cor_data,cor_column=cor_title,cor_len=len_corr,zip=session["logged_in"])
    else:
      zip=False
      return redirect("/login")


@app.route("/VisualizeData",methods=["GET","POST"])
def visual():
    if "logged_in" in session and session['logged_in']==True:
        zip=True
        sess=db.Sessions.find_one({"email":session["email"]})
        filename=sess["files"][len(sess["files"])-1]["filename"]
        if filename:
            df,titles=calldata(filename)

        else:
            df,titles=calldata("sampledata.csv")

        if request.method=="POST":
            print("FORM",request.form)

            x=request.form["x_axis"]
            y=request.form["y_axis"]
            hue=request.form["Hue"]
            graph=request.form["graph"]
            numerical_cols=numerical_col(df)
            print(numerical_cols)
    
            object_cols=object_col(df)
            print("object_cols",object_cols)
            sns.set(style='darkgrid')            
            if x in numerical_cols and y in numerical_cols:
                if graph=="Lineplot":
                    graphs("Lineplot",x,y,hue,df)

                elif graph=="Scatterplot":
                    graphs("Scatterplot",x,y,hue,df)

                elif graph=="relplot":
                    graphs("relplot",x,y,hue,df)

                elif graph=="lmplot":
                    graphs("lmplot",x,y,hue,df)

                elif graph=="jointplot":
                    graphs("jointplot",x,y,hue,df)

                elif graph=="Barplot":
                    graphs("Barplot",x,y,hue,df)
                

            elif x in numerical_cols and y in object_cols:
                if graph=="Barplot":
                    graphs("Barplot",y,x,hue,df)

                elif graph=="violenplot":
                    graphs("violenplot",y,x,hue,df)

                elif graph=="Boxplot":
                    graphs("Boxplot",y,x,hue,df)

            elif x in object_cols and y in numerical_cols:
                if graph=="Barplot":
                    graphs("Barplot",x,y,hue,df)

                elif graph=="violenplot":
                    graphs("violenplot",x,y,hue,df)

                elif graph=="Boxplot":
                    graphs("Boxplot",x,y,hue,df)

            elif x in object_cols and y in object_cols:
                flash("Both axis contains the feature having object datatype !","error")

            elif x=="None" and y=="None":

                if graph=="Pairplot":
                    graphs("Pairplot",x,y,hue,df)

                elif graph=="Heatmap":
                    graphs("Heatmap",x,y,hue,df)
            elif (x=="None" and y!="None") or ( y=="None" and x!="None"):
                if graph=="Countplot":
                    graphs("Countplot",x,y,hue,df)
                    
                elif graph=="Displot":
                    graphs("Displot",x,y,hue,df)
                


            return redirect(url_for("visual"))              
        

    return render_template("visual.html",data=df,length=len(titles),titles=titles,zip=zip)

@app.route("/logout")
def logout():
     if "logged_in" in session and session['logged_in']==True:
         
         session.pop("logged_in",None)
         session.pop("user",None)
         flash("Successfully Loged Out !","success")
         return redirect("/login")