from flask import Flask,render_template,request,redirect,url_for,flash,session
from datetime import date
import re,os,os.path,sys
import hashlib
import sqlite3
app = Flask(__name__)
app.secret_key = "HealthCorner"

def get_connection():
   """ Connecting the database """
   con = sqlite3.connect('HCwebsitedb.db')
   con.row_factory = sqlite3.Row
   return con

def passwordcheck(pwd):
  """ A strong password must contain 1 uppercase, 1 digit, 1 special """
  length = len(pwd) < 8
  digit = re.search(r"\d", pwd) is None
  uppercase = re.search(r"[A-Z]", pwd) is None
  lowercase = re.search(r"[a-z]", pwd) is None
  symbol = re.search(r"\W", pwd) is None
  password = not ( length or digit or uppercase or lowercase or symbol )
  return password

def changepass(pwd):
  """ Change input password into sha256 hashcode """
  hashpass = hashlib.sha256(pwd.encode('utf-8'))
  password = hashpass.hexdigest()
  return password

def pages(lo):
    med = 0
    page = 0
    no = 10
    for x in lo:
        med+=1
        if med == no:
            page+=1
            no+=10
    return page


@app.route('/', methods=['GET','POST'])
def home():
    try:
        if request.method == 'GET':
            return render_template('index.html')
        # else:     
    except Exception as e:
        pass

def checkemail(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"Select demail from doctor where demail='{email}'")
    doctor = cur.fetchone() is not None
    cur.execute(f"Select pemail from patient where pemail='{email}'")
    patient = cur.fetchone() is not None
    email = not ( doctor or patient )
    return email


@app.route('/register', methods=['GET','POST'])
def register():
    try:
        if request.method == 'GET':
            return render_template('register.html')
        else:
            registeruser = request.form['register']
            if registeruser == "patientreg":
                pname =  request.form['pname']
                pgender =  request.form['pgender']
                pemail =  request.form['pemail']
                pphone =  request.form['pphone']
                paddr =  request.form['paddr']
                ppwd =  request.form['ppwd']
                pcpwd =  request.form['pcpwd']
                pimg = "static/images/defaultprofile.PNG"
                emailchecker = checkemail(pemail)
                if emailchecker:
                    if ppwd == pcpwd:
                        pwdchecker = passwordcheck(ppwd)
                        if pwdchecker:
                            chpassword = changepass(ppwd)
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("insert into patient (pname,ppwd,pemail,pgender,pphone,paddr,pimg) values (?,?,?,?,?,?,?) ", (pname,chpassword,pemail,pgender,pphone,paddr,pimg))
                            conn.commit()
                            conn.close()
                            flash('Register has been complete successfully.')
                            return redirect('/login')
                        else:
                            flash('Password must be at leat 8words with 1 uppercase, 1 uppercase, 1 digit, 1 special(eg.!@#$%)')
                            n = True
                            return render_template('register.html', pname = pname, pemail = peamil, pphone = pphone, paddr = paddr, n = n)
                    else:
                        flash('Passwords are not match')
                        n = True
                        return render_template('register.html', pname = pname, pemail = peamil, pphone = pphone, paddr = paddr, n = n)
                else:
                    flash(f'Email already in used')
                    n = True
                    return render_template('register.html', pname = pname, pphone = pphone, paddr = paddr, n = n)
            if registeruser == "doctorreg":
                dname =  request.form['dname']
                dgender =  request.form['dgender']
                demail =  request.form['demail']
                dphone =  request.form['dphone']
                daddr =  request.form['daddr']
                specialist =  request.form['specialist']
                hospitalname = request.form['hospitalname']
                dpwd =  request.form['dpwd']
                dcpwd =  request.form['dcpwd']
                dimg = "static/images/defaultprofile.PNG"
                emailchecker = checkemail(demail)
                if emailchecker:
                    if dpwd == dcpwd:
                        pwdchecker = passwordcheck(dpwd)
                        if pwdchecker:
                            chpassword = changepass(dpwd)
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("insert into doctor (dname,dpwd,demail,dgender,dphone,daddr,hospitalname,speciality,dimg) values (?,?,?,?,?,?,?,?,?) ", (dname,chpassword,demail,dgender,dphone,daddr,hospitalname,specialist,dimg))
                            conn.commit()
                            conn.close()
                            flash('Register has been complete successfully.')
                            return redirect('/login')
                        else:
                            flash('Password must be at leat 8words with 1 uppercase, 1 digit, 1 special(eg.!@#$%)')
                            d = True
                            return render_template('register.html', dname = dname, demail = demail, dphone = dphone, daddr = daddr, specialist = specialist, hospitalname = hospitalname, d = d)
                    else:
                        flash('Passwords are not match')
                        d = True
                        return render_template('register.html', dname = dname, demail = demail, dphone = dphone, daddr = daddr, specialist = specialist, hospitalname = hospitalname, d = d)
                else:
                    flash('Email already in used')
                    d = True
                    return render_template('register.html', dname = dname, dphone = dphone, daddr = daddr, specialist = specialist, hospitalname = hospitalname, d = d)
    except Exception as e:
        pass

@app.route('/login', methods=['GET','POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            inputbutton = request.form['submit']
            if inputbutton:
                loginemail = request.form['email']
                password = request.form['pw']
                loginpassword = changepass(password)
                conn = get_connection()
                cur = conn.cursor()
                try:
                    cur.execute(f"Select * from admin where aemail='{loginemail}'")
                    admin = cur.fetchone()
                    if loginpassword == admin['apwd']:
                        session['login'] = True
                        session['aid'] = admin['aid']
                        return redirect('/adminhome')
                except Exception as error:
                    pass
                try:
                    cur.execute(f"Select * from doctor where demail='{loginemail}'")
                    doctor = cur.fetchone()
                    if loginpassword == doctor['dpwd']:
                        session['login'] = True
                        session['did'] = doctor['did']
                        session['user'] = "doctor"
                        dimg = doctor['dimg']
                        session['image'] = dimg
                        return redirect('/')
                except Exception as error:
                    pass
                try:
                    cur.execute(f"Select * from patient where pemail='{loginemail}'")
                    patient = cur.fetchone()
                    if loginpassword == patient['ppwd']:
                        session['login'] = True
                        session['pid'] = patient['pid']
                        session['user'] = "patient"
                        pimg = patient['pimg']
                        session['image'] = pimg
                        return redirect('/')
                except Exception as error:
                    pass
                flash("Your Email or Password is incorrect.")
                return redirect('/login')
    except Exception as error:
        print(f'{error}')

@app.route('/admindeleteblog:<bid>', methods = ['POST'])
def admindeleteblog(bid):
    try:
        with get_connection() as connection:
            cur = connection.cursor()
            cur.execute(f"DELETE from blog where blogid='{bid}'")
            connection.commit()
            flash("Deleting blog information is successful.")
            return redirect(url_for('adminbloginfo'))
    except sqlite3.Error as error:
        print(f'{error}-->{error.__class__.__name__}')
        
@app.route('/admindeletecomment:<cid>', methods = ['POST'])
def admindeletecomment(cid):
    try:
        with get_connection() as connection:
            cur = connection.cursor()
            cur.execute(f"DELETE from comment where commentid='{cid}'")
            connection.commit()
            flash('Deleting comment is successful.')
            return redirect(url_for('adminbloginfo'))
    except sqlite3.Error as error:
        print(f'{error}-->{error.__class__.__name__}')
    

@app.route('/forgotpwd', methods=['GET','POST'])
def forgotpwd():
    try:
        if request.method == 'GET':
            f = False
            return render_template('forgotpwd.html', f = f)
        else:
            inputbtn = request.form['submit']
            if inputbtn == "Verify":
                email = request.form['email']
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(f"Select * from doctor where demail='{email}'")
                doctor = cur.fetchone() is not None
                cur.execute(f"Select * from patient where pemail='{email}'")
                patient = cur.fetchone() is not None
                if doctor == True or patient == True:
                    f = True
                    return render_template('forgotpwd.html', f = f, email = email)
                else:
                    flash("Email does not exit. Please register.")
                    return redirect('/register')
            elif inputbtn == "Reset":
                email = request.form['hemail']
                password = request.form['pw']
                cpassword = request.form['cpw']
                if password == cpassword:
                        pwdchecker = passwordcheck(password)
                        if pwdchecker:
                            chpassword = changepass(password)
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(f"Select * from doctor where demail='{email}'")
                            doctorinfo = cur.fetchone() is not None
                            if doctorinfo == True:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute(f"Select dpwd from doctor where demail='{email}'")
                                doctor = cur.fetchone()
                                pwd = doctor['dpwd']
                                if pwd == chpassword:
                                    flash("You cannot use the old Password! Please Use New One!")
                                    f = True
                                    return render_template('forgotpwd.html', f = f, email = email)
                            cur.execute(f"Select * from patient where pemail='{email}'")
                            patientinfo = cur.fetchone() is not None
                            if patientinfo == True:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute(f"Select ppwd from patient where pemail='{email}'")
                                patient = cur.fetchone()
                                pwd = patient['ppwd']
                                if pwd == chpassword:
                                    flash("You cannot use the old Password! Please Use New One!")
                                    f = True
                                    return render_template('forgotpwd.html', f = f, email = email)
                            if doctorinfo == True and patientinfo == False:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute(f"update doctor set dpwd='{chpassword}' where demail='{email}'")
                                conn.commit()
                                flash('Password Reset Successful')
                                return redirect(url_for('login'))
                            if patientinfo == True and doctorinfo == False:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute(f"update patient set ppwd='{chpassword}' where pemail='{email}'")
                                conn.commit()
                                flash('Password Reset Successful')
                                return redirect(url_for('login'))
                        else:
                            flash('Password must be at leat 8words with 1 uppercase, 1 uppercase, 1 digit, 1 special(eg.!@#$%)')
                            f = True
                            return render_template('forgotpwd.html', f = f, email = email)
                else:
                    flash('Passwords are not match')
                    f = True
                    return render_template('forgotpwd.html', f = f, email = email)      
                            
    except Exception as e:
        pass


@app.route('/doctor', methods=['GET','POST'])
def doctor():
    try:
        if request.method == 'GET':
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("Select * from doctor")
            doctors = cur.fetchall()
            return render_template('doctors.html', doctor = doctors)
        else:
            try:
                con = get_connection()
                cur=con.cursor()
                if request.form['docname'] != '':
                    docnamesearch = request.form['docname']

                    cur.execute('select * from doctor')
                    docdata = cur.fetchall()
                    docdict1 = {}
                    matchdoc = []
                    for line in docdata:
                        docdict1[str(line[0])]=str(line[1])

                    for did, dname in docdict1.items():
                        match = re.search(docnamesearch, dname, re.IGNORECASE)
                        if match:
                            matchdoc.append(did)

                    if request.form['speciality'] != '':
                        specialitysearch = request.form['speciality']

                        docdict2 = {}
                        for line in docdata:
                            docdict2[str(line[0])]=str(line[9])

                        for did, speciality in docdict2.items():
                            match = re.search(specialitysearch, speciality, re.IGNORECASE)
                            if match:
                                matchdoc.append(did)
                    
                        if request.form['hosname'] != '':
                            hosnamesearch = request.form['hosname']

                            docdict3 = {}
                            for line in docdata:
                                docdict3[str(line[0])]=str(line[7])

                            for did, hospitalname in docdict3.items():
                                match = re.search(hosnamesearch, hospitalname, re.IGNORECASE)
                                if match:
                                    matchdoc.append(did)

                            if request.form['gender'] != '':
                                gendersearch = request.form['gender']

                                docdict4 = {}
                                for line in docdata:
                                    docdict4[str(line[0])]=str(line[8])

                                for did, gender in docdict4.items():
                                    if gender == gendersearch:
                                        matchdoc.append(did)
                    docfounddata = {}
                    if matchdoc != []:
                        for i in matchdoc:
                            cur.execute('select * from doctor where did=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['did'] not in docfounddata.keys():
                                    docfounddata[one['did']]=[]
                                    docfounddata[one['did']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect(url_for('doctor'))

                    matchdocinfo = []
                    for data in docfounddata.values():
                        matchdocinfo.append(data)
                    return render_template('doctors.html', matchdocinfo = matchdocinfo )

                elif request.form['speciality'] != '':
                    specialitysearch = request.form['speciality']

                    cur.execute('select * from doctor')
                    docdata = cur.fetchall()
                    matchdoc = []

                    docdict2 = {}
                    for line in docdata:
                        docdict2[str(line[0])]=str(line[9])

                    for did, speciality in docdict2.items():
                        match = re.search(specialitysearch, speciality, re.IGNORECASE)
                        if match:
                            matchdoc.append(did)
                    
                    if request.form['hosname'] != '':
                        hosnamesearch = request.form['hosname']

                        docdict3 = {}
                        for line in docdata:
                            docdict3[str(line[0])]=str(line[7])

                        for did, hospitalname in docdict3.items():
                            match = re.search(hosnamesearch, hospitalname, re.IGNORECASE)
                            if match:
                                matchdoc.append(did)

                        if request.form['gender'] != '':
                            gendersearch = request.form['gender']

                            docdict4 = {}
                            for line in docdata:
                                docdict4[str(line[0])]=str(line[8])

                            for did, gender in docdict4.items():
                                if gender == gendersearch:
                                    matchdoc.append(did)
                    docfounddata = {}
                    if matchdoc != []:
                        for i in matchdoc:
                            cur.execute('select * from doctor where did=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['did'] not in docfounddata.keys():
                                    docfounddata[one['did']]=[]
                                    docfounddata[one['did']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect(url_for('doctor'))

                    matchdocinfo = []
                    for data in docfounddata.values():
                        matchdocinfo.append(data)
                    return render_template('doctors.html', matchdocinfo = matchdocinfo )

                elif request.form['hosname'] != '':
                    hosnamesearch = request.form['hosname']

                    cur.execute('select * from doctor')
                    docdata = cur.fetchall()
                    matchdoc = []

                    docdict3 = {}
                    for line in docdata:
                        docdict3[str(line[0])]=str(line[7])

                    for did, hospitalname in docdict3.items():
                        match = re.search(hosnamesearch, hospitalname, re.IGNORECASE)
                        if match:
                            matchdoc.append(did)

                    if request.form['gender'] != '':
                        gendersearch = request.form['gender']

                        docdict4 = {}
                        for line in docdata:
                            docdict4[str(line[0])]=str(line[8])

                        for did, gender in docdict4.items():
                            if gender == gendersearch:
                                matchdoc.append(did)
                    docfounddata = {}
                    if matchdoc != []:
                        for i in matchdoc:
                            cur.execute('select * from doctor where did=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['did'] not in docfounddata.keys():
                                    docfounddata[one['did']]=[]
                                    docfounddata[one['did']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect(url_for('doctor'))

                    matchdocinfo = []
                    for data in docfounddata.values():
                        matchdocinfo.append(data)
                    return render_template('doctors.html', matchdocinfo = matchdocinfo )

                elif request.form['gender'] != '':
                    gendersearch = request.form['gender']

                    cur.execute('select * from doctor')
                    docdata = cur.fetchall()
                    matchdoc = []

                    docdict4 = {}
                    for line in docdata:
                        docdict4[str(line[0])]=str(line[8])

                    for did, gender in docdict4.items():
                        if gender == gendersearch:
                            matchdoc.append(did)

                    docfounddata = {}
                    if matchdoc != []:
                        for i in matchdoc:
                            cur.execute('select * from doctor where did=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['did'] not in docfounddata.keys():
                                    docfounddata[one['did']]=[]
                                    docfounddata[one['did']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect(url_for('doctor'))

                    matchdocinfo = []
                    for data in docfounddata.values():
                        matchdocinfo.append(data)
                    return render_template('doctors.html', matchdocinfo = matchdocinfo )

                else:
                    flash('Nothing is found!')
                    return redirect(url_for('doctor'))

            except TypeError as err:
                flash('Nothing is found!')
                return redirect(url_for('doctor'))
    except Exception as e:
        pass

@app.route('/contact', methods=['GET','POST'])
def contact():
    try:
        if request.method == 'GET':
            return render_template('contact.html')
        else:
            feedbackname = request.form['fname']
            feedbackemail = request.form['email']
            feedbackmessage = request.form['message']
            if session['user'] == "patient":
                pid = session['pid']
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute("INSERT into feedback (pid,fbmsg) VALUES (?,?)",(pid,feedbackmessage))
                    connection.commit()
                return render_template('contact.html')
            elif session['user'] == "doctor":
                did = session['did']
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute("INSERT into feedback (did,fbmsg) VALUES (?,?)",(did,feedbackmessage))                
                    connection.commit()
                return render_template('contact.html')
    except TypeError as e:
        flash('Please Login')
        return redirect(url_for('login'))
    except KeyError as e:
        flash('Please Login')
        return redirect(url_for('login'))

@app.route('/aboutus', methods=['GET','POST'])
def aboutus():
    try:
        if request.method == 'GET':
            return render_template('aboutus.html')
        # else:     
    except Exception as e:
        pass

@app.route('/userviewblog:<no>', methods=['GET'])
def userviewblog(no):
    try:
        if 'login' in session:
            start = int(no) * 10
            if session['user'] == "patient":
                pid = session['pid']
                did = 'None'
            elif session['user'] == "doctor":
                did = session['did']
                pid = 'None'
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("Select * from blog")
                blog = cur.fetchall()
                page = pages(blog)
                cur.execute(f"Select * from blog LIMIT 10 OFFSET {start}")
                bloginfo = cur.fetchall()
                cur.execute("Select * from comment")
                commentinfo = cur.fetchall()
                cur.execute(f"Select * from patient")
                patient = cur.fetchall()
                cur.execute(f"Select * from doctor")
                doctor = cur.fetchall()
            return render_template('userviewpost.html', blogs = bloginfo, comments = commentinfo, pid = pid, patient = patient, did = did, doctor = doctor, page = page)
        else:
            flash('Please **Login** before viewing blogs!')
            return render_template('login.html')
    except Exception as e:
        pass
        
@app.route('/like:<no>', methods=['GET','POST'])
def like(no):
    try:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(f"Select bloglike from blog where blogid={no}")
            blog = cur.fetchone()
            bloginfo = blog['bloglike']
            like = bloginfo
            like += 1
            cur.execute(f"update blog set bloglike='{like}' where blogid={no}")
            con.commit()
            return redirect('/userviewblog:0')
    except Exception as e:
        pass

@app.route('/unlike:<no>', methods=['GET','POST'])
def unlike(no):
    try:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(f"Select blogunlike from blog where blogid={no}")
            blog = cur.fetchone()
            bloginfo = blog['blogunlike']
            unlike = bloginfo
            unlike += 1
            cur.execute(f"update blog set blogunlike='{unlike}' where blogid={no}")
            con.commit()
            return redirect('/userviewblog:0')
    except Exception as e:
        pass

@app.route('/useruploadblog', methods=['GET','POST'])
def useruploadblog():
    try:
        if request.method == 'GET':
             return render_template('user_upload_post.html')
        else:
            blogtitle = request.form['blog_title']
            bloginfo = request.form['bloginfo']
            img = request.files['image']
            video = request.files['video']
            blogdate = date.today()
            like = 0
            unlike = 0
            imgfile = os.path.join(img.filename)
            vidfile = os.path.join(video.filename)
            try:
                con = get_connection()
                cur=con.cursor()
                if imgfile != '':
                    img = request.files['image']
                    img.save(os.path.join('static/images/',img.filename))
                    fpimg = os.path.join('static/images/',img.filename)
                    if vidfile != '':
                        video = request.files['video']
                        video.save(os.path.join('static/videos/',video.filename))
                        fpvideo = os.path.join('static/videos/',video.filename)
                        if session['pid']:
                            pid = session['pid']
                            
                            cur.execute('Insert into blog (blogtitle,bloginfo,img,video,blogdate,pid,bloglike,blogunlike) values (?,?,?,?,?,?,?,?)', (blogtitle,bloginfo,fpimg,fpvideo,blogdate,pid,like,unlike))
                            con.commit()
                        elif session['did']:
                            did = session['did']
                            cur.execute('Insert into blog (blogtitle,bloginfo,img,video,blogdate,did,bloglike,blogunlike) values (?,?,?,?,?,?,?,?)', (blogtitle,bloginfo,fpimg,fpvideo,blogdate,did,like,unlike))
                            con.commit()
                        return redirect('/userviewblog:0')
                    else:
                        if session['pid']:
                            pid = session['pid']
                            cur.execute('Insert into blog (blogtitle,bloginfo,img,blogdate,pid,bloglike,blogunlike) values (?,?,?,?,?,?,?)', (blogtitle,bloginfo,fpimg,blogdate,pid,like,unlike))
                            con.commit()   
                        elif session['did']:
                            did = session['did']
                            cur.execute('Insert into blog (blogtitle,bloginfo,img,blogdate,did,bloglike,blogunlike) values (?,?,?,?,?,?,?)', (blogtitle,bloginfo,fpimg,blogdate,did,like,unlike))
                            con.commit()
                        return redirect('/userviewblog:0')
                else:
                    if vidfile != '':
                        video = request.files['video']
                        video.save(os.path.join('static/videos/',video.filename))
                        fpvideo = os.path.join('static/videos/',video.filename)
                        if session['pid']:
                            pid = session['pid']
                            cur.execute('Insert into blog (blogtitle,bloginfo,video,blogdate,pid,bloglike,blogunlike) values (?,?,?,?,?,?,?)', (blogtitle,bloginfo,fpvideo,blogdate,pid,like,unlike))
                            con.commit()   
                        elif session['did']:
                            did = session['did']
                            cur.execute('Insert into blog (blogtitle,bloginfo,video,blogdate,did,bloglike,blogunlike) values (?,?,?,?,?,?,?)', (blogtitle,bloginfo,fpvideo,blogdate,did,like,unlike))
                            con.commit()
                        return redirect('/userviewblog:0')
                    else:
                        if session['pid']:
                            pid = session['pid']
                            cur.execute('Insert into blog (blogtitle,bloginfo,blogdate,pid,bloglike,blogunlike) values (?,?,?,?,?,?)', (blogtitle,bloginfo,blogdate,pid,like,unlike))
                            con.commit()   
                        elif session['did']:
                            did = session['did']
                            cur.execute('Insert into blog (blogtitle,bloginfo,blogdate,did,bloglike,blogunlike) values (?,?,?,?,?,?)', (blogtitle,bloginfo,blogdate,did,like,unlike))
                            con.commit()
                        return redirect('/userviewblog:0')
            except TypeError as err:
                flash('fail')
                return redirect(url_for('useruploadblog'))
    except Exception as e:
        pass

@app.route('/usereditblog:<bid>', methods=['GET','POST'])
def usereditblog(bid):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select * from blog where blogid='{bid}'")
                bloginfo = cur.fetchone()
                return render_template('user_edit_post.html', blog = bloginfo)
        else:
            blog_title = request.form['blog_title']
            blog_info = request.form['blog_info']
            blogdate = date.today()
            try:
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute(f"update blog set blogtitle='{blog_title}', bloginfo='{blog_info}', blogdate='{blogdate}' where blogid={bid}")
                    connection.commit()
                    flash('Edit Blog Info Successful')
                    return redirect('/usereditblog:0')
            except sqlite3.Error as error:
                    print (f'{error}---->{error.__class__.__name__}')
    except Exception as e:
        pass

@app.route('/userdelblog:<bid>', methods=['POST'])
def userdelblog(bid):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"delete from blog where blogid='{bid}'")
        conn.commit()
        flash("Deleting is successful.")
        return redirect('/userviewblog:0')
    except Exception as e:
        pass

@app.route('/usercomment:<bid>', methods=['POST'])
def usercomment(bid):
    try:
        commentinfo = request.form['commentinfo']
        if session['user'] == "patient":
            pid = session['pid']
            try:
                connection = get_connection()
                cur = connection.cursor()
                cur.execute("insert into comment (commentinfo,blogid,pid) values (?,?,?)", (commentinfo,bid,pid))
                connection.commit()
            except sqlite3.Error as error:
                print(f'{error}----->{error.__class__.__name__}')
            except TypeError as error:
                pass
            return redirect('/userviewblog:0')
        elif session['user'] == "doctor":
            did = session['did']
            try:
                connection = get_connection()
                cur = connection.cursor()
                cur.execute("insert into comment (commentinfo,blogid,did) values (?,?,?)", (commentinfo,bid,did))
                connection.commit()
            except sqlite3.Error as error:
                print(f'{error}----->{error.__class__.__name__}')
            return redirect('/userviewblog:0')
    except Exception as e:
        pass



@app.route('/medicallist:<no>', methods=['GET','POST'])
def medicallistno(no):
    try:
        if request.method == 'GET':
            start = int(no) * 10
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("Select * from medical")
                medicalinfo = cur.fetchall()
                page = pages(medicalinfo)
                cur = con.cursor()
                cur.execute(f"Select * from medical LIMIT 10 OFFSET {start}")
                medicalinfo = cur.fetchall()
                pagi = True
                return render_template('medicallist.html', mediinfo = medicalinfo, page = page, pagi = pagi)
        else:
            try:
                pagi = False
                con = get_connection()
                cur=con.cursor()
                if request.form['medikeyword'] != '':
                    medisearch = request.form['medikeyword']

                    cur.execute('select * from medical')
                    medidata = cur.fetchall()
                    medidict1 = {}
                    matchmedi = []
                    for line in medidata:
                        medidict1[str(line[0])]=str(line[1])

                    for medicalid, medicaltitle in medidict1.items():
                        match = re.search(medisearch, medicaltitle, re.IGNORECASE)
                        if match:
                            matchmedi.append(medicalid)

                    medidict2 = {}
                    for line in medidata:
                        medidict2[str(line[0])]=str(line[2])

                    for medicalid, medicalinfo in medidict2.items():
                        match = re.search(medisearch, medicalinfo, re.IGNORECASE)
                        if match:
                            matchmedi.append(medicalid)

                    
                    medifounddata = {}
                    if matchmedi != []:
                        for i in matchmedi:
                            cur.execute('select * from medical where medicalid=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['medicalid'] not in medifounddata.keys():
                                    medifounddata[one['medicalid']]=[]
                                    medifounddata[one['medicalid']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect('/medicallist:0')

                    matchmediinfo = []
                    for data in medifounddata.values():
                        matchmediinfo.append(data)
                    return render_template('medicallist.html', matchmediinfo = matchmediinfo, pagi = pagi )

                else:
                    flash('Nothing is found!')
                    return redirect('/medicallist:0')
            except TypeError as err:
                flash('Nothing is found!')
                return redirect('/medicallist:0')
    except Exception as e:
        pass

@app.route('/medicalinfo:<medical_title>:<medical_id>', methods=['GET','POST'])
def medicalinfo(medical_title,medical_id):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select medicalinfo from medical where medicalid='{medical_id}'")
                medicalinfo = cur.fetchone()
                return render_template('medicalinfo.html', mediinfo = medicalinfo, title = medical_title, mid = medical_id)
        #else:
    except Exception as e:
        pass
    
@app.route('/diseaselist:<no>', methods=['GET','POST'])
def diseaselistno(no):
    try:
        if request.method == 'GET':
            start = int(no) * 10
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("Select * from disease")
                diseaseinfo = cur.fetchall()
                page = pages(diseaseinfo)
                cur = con.cursor()
                cur.execute(f"Select * from disease LIMIT 10 OFFSET {start}")
                diseaseinfo = cur.fetchall()
                pagi = True
                return render_template('diseaselist.html', disinfo = diseaseinfo, page = page, pagi = pagi)
        else:
            try:
                pagi = False
                con = get_connection()
                cur=con.cursor()
                if request.form['disesasename'] != '':
                    dissearch = request.form['disesasename']

                    cur.execute('select * from disease')
                    disdata = cur.fetchall()
                    disdict1 = {}
                    matchdis = []
                    for line in disdata:
                        disdict1[str(line[0])]=str(line[1])

                    for disid, disname in disdict1.items():
                        match = re.search(dissearch, disname, re.IGNORECASE)
                        if match:
                            matchdis.append(disid)

                    if request.form['keyword'] != '':

                        diskeyword = request.form['keyword']

                        disdict2 = {}
                        for line in disdata:
                            disdict2[str(line[0])]=str(line[2])
                        for disid, disdescription in disdict2.items():
                            match = re.search(diskeyword, disdescription, re.IGNORECASE)
                            if match:
                                matchdis.append(disid)

                        disdict3 = {}
                        for line in disdata:
                            disdict3[str(line[0])]=str(line[3])
                        for disid, dissymptoms in disdict3.items():
                            match = re.search(diskeyword, dissymptoms, re.IGNORECASE)
                            if match:
                                matchdis.append(disid)

                        disdict4 = {}
                        for line in disdata:
                            disdict4[str(line[0])]=str(line[4])
                        for disid, treatment in disdict4.items():
                            match = re.search(diskeyword, treatment, re.IGNORECASE)
                            if match:
                                matchdis.append(disid)

                    disfounddata = {}
                    if matchdis != []:
                        for i in matchdis:
                            cur.execute('select * from disease where disid=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['disid'] not in disfounddata.keys():
                                    disfounddata[one['disid']]=[]
                                    disfounddata[one['disid']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect('/diseaselist:0')

                    matchdisinfo = []
                    for data in disfounddata.values():
                        matchdisinfo.append(data)
                    return render_template('diseaselist.html', matchdisinfo = matchdisinfo, pagi = pagi )

                elif request.form['keyword'] != '':

                    cur.execute('select * from disease')
                    disdata = cur.fetchall()
                    disdict1 = {}
                    matchdis = []
                    for line in disdata:
                        disdict1[str(line[0])]=str(line[1])

                    diskeyword = request.form['keyword']

                    disdict2 = {}
                    for line in disdata:
                        disdict2[str(line[0])]=str(line[2])
                    for disid, disdescription in disdict2.items():
                        match = re.search(diskeyword, disdescription, re.IGNORECASE)
                        if match:
                            matchdis.append(disid)

                    disdict3 = {}
                    for line in disdata:
                        disdict3[str(line[0])]=str(line[3])
                    for disid, dissymptoms in disdict3.items():
                        match = re.search(diskeyword, dissymptoms, re.IGNORECASE)
                        if match:
                            matchdis.append(disid)

                    disdict4 = {}
                    for line in disdata:
                        disdict4[str(line[0])]=str(line[4])
                    for disid, treatment in disdict4.items():
                        match = re.search(diskeyword, treatment, re.IGNORECASE)
                        if match:
                            matchdis.append(disid)

                    disfounddata = {}
                    if matchdis != []:
                        for i in matchdis:
                            cur.execute('select * from disease where disid=?',(i, ))
                            founddata = cur.fetchall()
                            for one in founddata:
                                if one['disid'] not in disfounddata.keys():
                                    disfounddata[one['disid']]=[]
                                    disfounddata[one['disid']].append(one)
                    else:
                        flash('Nothing is found!')
                        return redirect('/diseaselist:0')
                    matchdisinfo = []
                    for data in disfounddata.values():
                        matchdisinfo.append(data)
                    return render_template('diseaselist.html', matchdisinfo = matchdisinfo, pagi = pagi )
                else:
                    flash('Nothing is found!')
                    return redirect('/diseaselist:0')
            except TypeError as err:
                flash('Nothing is found!')
                return redirect('/diseaselist:0')
    except Exception as e:
        pass

@app.route('/diseaseinfo:<disease_name>:<disease_id>', methods=['GET','POST'])
def diseaseinfo(disease_name,disease_id):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select * from disease where disid='{disease_id}'")
                diseaseinfo = cur.fetchone()
            return render_template('diseaseinfo.html', disinfo = diseaseinfo, name = disease_name, did = disease_id)
        # else:     
    except Exception as e:
        pass


@app.route('/doctorprofile:<did>', methods=['GET','POST'])
def doctorprofile(did):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"select * from doctor where did='{did}'")
                doctor = cur.fetchone()
            return render_template('doctorprofile.html', doctor = doctor)
        # else:     
    except Exception as e:
        pass

@app.route('/editdocprofile:<did>', methods=['GET','POST'])
def editdocprofile(did):
    try:
        if request.method == 'GET':
            with get_connection() as connection:
                cur = connection.cursor()
                cur.execute('SELECT * FROM doctor WHERE did=?',(did,))
                doctor = cur.fetchone()
            return render_template('editdoctorprofile.html', doctorinfo = doctor)
        else:
            dname = request.form['dname']
            dgender = request.form['dgender']
            demail = request.form['demail']
            daddress = request.form['daddress']
            dphone = request.form['dphone']
            hospitalname = request.form['hospitalname']
            specilist = request.form['specilist']
            dimg = request.files['image']
            imgfile = os.path.join(dimg.filename)
            if imgfile == '': 
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute(f"UPDATE doctor set dname='{dname}', dgender='{dgender}', demail='{demail}', daddr='{daddress}', dphone='{dphone}', hospitalname='{hospitalname}', speciality='{specilist}' WHERE did='{did}'")
                    connection.commit()
                    return redirect(f'/doctorprofile:{did}')
            elif imgfile != '':
                dimg.save(os.path.join('static/images/',dimg.filename))
                dimgpath = os.path.join('static/images/',dimg.filename)
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute(f"UPDATE doctor set dname='{dname}', dgender='{dgender}', demail='{demail}', daddr='{daddress}', dphone='{dphone}', hospitalname='{hospitalname}', speciality='{specilist}', dimg='{dimgpath}' WHERE did='{did}'")
                    connection.commit()
                    session['image'] = dimgpath
                    return redirect(f'/doctorprofile:{did}')
    except Exception as e:
        pass
    
@app.route('/editpatientprofile:<pid>', methods=['GET','POST'])
def editpatientprofile(pid):
    try:
        if request.method == 'GET':
            with get_connection() as connection:
                cur = connection.cursor()
                cur.execute('SELECT * FROM patient WHERE pid=?',(pid,))
                patient = cur.fetchone()
                return render_template('editpatientprofile.html', patientdata = patient)
        else:
            pname = request.form['pname']
            pgender = request.form['pgender']
            pemail = request.form['pemail']
            paddress = request.form['paddress']
            pphone = request.form['pphone']
            healthinfo = request.form['healthinfo']
            pimg = request.files['image']
            imgfile = os.path.join(pimg.filename)
            if imgfile == '':    
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute(f"UPDATE patient set pname='{pname}', pgender='{pgender}', pemail='{pemail}', paddr='{paddress}', pphone='{pphone}', healthinfo='{healthinfo}' WHERE pid='{pid}'")
                    connection.commit()
                    return redirect(f'/patientprofile:{pid}')
            elif imgfile != '':
                pimg.save(os.path.join('static/images/',pimg.filename))
                pimgpath = os.path.join('static/images/',pimg.filename)
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute(f"UPDATE patient set pname='{pname}', pgender='{pgender}', pemail='{pemail}', paddr='{paddress}', pphone='{pphone}', healthinfo='{healthinfo}', pimg='{pimgpath}' WHERE pid='{pid}'")
                    connection.commit()
                    session['image'] = pimgpath
                    return redirect(f'/patientprofile:{pid}')
    except Exception as e:
        pass

@app.route('/patientprofile:<pid>', methods=['GET','POST'])
def patientprofile(pid):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"select * from patient where pid='{pid}'")
                patient = cur.fetchone()
            return render_template('patientprofile.html', patient = patient)
        # else:     
    except Exception as e:
        pass

@app.route('/adminhome', methods=['GET','POST'])
def adminhome():
    try:
        if request.method == 'GET':
            return render_template('adminhome.html')
        # else:     
    except Exception as e:
        pass

@app.route('/admindoctors', methods=['GET'])
def admindoctors():
    try:
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('select * from doctor')
                doctor = cur.fetchall()
                return render_template('admin_edit_doc_info.html', d=doctor)
        except sqlite3.Error as err:
                print(f'{err}{err.__class__.name__}')
        # else:     
    except Exception as e:
        pass

@app.route('/deletedoctorinfo:<did>', methods=['POST'])
def deletedoctorinfo(did):
    try:
        with get_connection() as connection:
            cur = connection.cursor()
            cur.execute(f"delete from doctor where did='{did}'")
            connection.commit()
            flash('Deleting a doctor information is successful.')
            return redirect(url_for('admindoctors'))
    except sqlite3.Error as error:
        print(f'{error}-->{error.__class__.__name__}')
        
@app.route('/adminpatients', methods=['GET','POST'])
def adminpatients():
    try:
        if request.method == 'GET':
            try:
                with get_connection() as con:
                    cur = con.cursor()
                    cur.execute('select * from patient')
                    patient = cur.fetchall()
                    return render_template('admin_edit_patient_info.html', p=patient)
            except sqlite3.Error as err:
                print(f'{err}{err.__class__.name__}')
        # else:     
    except Exception as e:
        pass

@app.route('/deletepatientinfo:<pid>', methods=['POST'])
def deletepatientinfo(pid):
    try:
        try:
            with get_connection() as connection:
                cur = connection.cursor()
                cur.execute(f"delete from patient where pid='{pid}'")
                connection.commit()
                flash('Deleting a patient information is successful.')
                return redirect('/adminpatients')
        except sqlite3.Error as error:
            print(f'{error}-->{error.__class__.__name__}')
    except Exception as e:
        raise e

@app.route('/adminmedicallist', methods=['GET'])
def adminmedicallist():
    try:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("Select medicalid,medicaltitle from medical")
            medicalinfo = cur.fetchall()
            return render_template('adminmedicallist.html', mediinfo = medicalinfo )     
    except Exception as e:
        pass

@app.route('/adminmedicalinfo/<medical_title>:<medical_id>', methods=['GET','POST'])
def adminmedicalinfo(medical_title,medical_id):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select medicalinfo from medical where medicalid='{medical_id}'")
                medicalinfo = cur.fetchone()
                return render_template('adminmedicalinfo.html', mediinfo = medicalinfo, title = medical_title, mid = medical_id)
        #else:
    except Exception as e:
        pass

@app.route('/admininsertmedicalinfo', methods=['GET','POST'])
def admininsertmedicalinfo():
    try:
        if request.method == 'GET':
            return render_template('admin_insert_medi_info.html')
        else:
            medical_title = request.form['medi_title']
            medical_info = request.form['medi_info']
            medidate = date.today() #or input(datetime.date)
            aid = session['aid']
            try:
                connection = get_connection()
                cur = connection.cursor()
                cur.execute("insert into medical (medicaltitle,medicalinfo,medidate,aid) values (?,?,?,?)", (medical_title,medical_info,medidate,aid))
                connection.commit()
            except sqlite3.Error as error:
                print(f'{error}----->{error.__class__.__name__}')
            flash('Insert Medical Info Successful')
            return redirect(url_for('adminmedicallist'))
    except Exception as e:
        pass

@app.route('/adminupdatemedicalinfo:<mid>', methods=['GET','POST'])
def adminupdatemedicalinfo(mid):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select * from medical where medicalid='{mid}'")
                medicalinfo = cur.fetchone()
            return render_template('admin_update_medi_info.html', mediinfo = medicalinfo, mid = mid)
        else:
            medical_title = request.form['medi_title']
            medical_info = request.form['medi_info']
            medidate = date.today()
            hmedical_info = request.form['hmifo']
            if medical_info == '':
                medical_info = hmedical_info
            try:
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute(f"update medical set medicaltitle='{medical_title}', medicalinfo='{medical_info}', medidate='{medidate}' where medicalid={mid}")
                    connection.commit()
                    flash('Edit Medical Info Successful')
                    return redirect(f'/adminmedicalinfo/{medical_title}:{mid}')
            except sqlite3.Error as error:
                    print (f'{error}---->{error.__class__.__name__}')
    except Exception as e:
        pass

@app.route('/adminmedicaldel:<mid>', methods=['POST'])
def adminmedicaldel(mid):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"delete from medical where medicalid='{mid}'")
        conn.commit()
        conn.close()
        flash('Deleting a medical information is successful.')
        return redirect(url_for('adminmedicallist'))
    except Exception as e:
        pass

@app.route('/adminlist', methods=['GET','POST'])
def adminlist():
    try:
        if request.method == 'GET':
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("Select * from admin")
            admins = cur.fetchall()
            return render_template('admin_view_admin_info.html', admin = admins)
        # else:     
    except Exception as e:
        pass

@app.route('/admindel:<aid>', methods=['POST'])
def admindel(aid):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"delete from admin where aid='{aid}'")
        conn.commit()
        conn.close()
        flash('Deleting an admin information is successful.')
        return redirect(url_for('adminlist'))
    except Exception as e:
        pass

@app.route('/adminupdate:<aid>', methods=['GET','POST'])
def adminupdate(aid):
    try:
        if request.method == 'GET':
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(f"Select * from admin where aid='{aid}'")
            admins = cur.fetchone()
            return render_template('admin_edit_admin_info.html', admin = admins)
        else:
            aname = request.form['aname']
            aphone = request.form['aphone']
            aemail = request.form['aemail']
            try:
                with get_connection() as connection:
                    cur = connection.cursor()
                    cur.execute("update admin set aname=?, aphone=?, aemail=? where aid=?", (aname,aphone,aemail,aid))
                    connection.commit()
                    flash('Edit Admin Info Successful')
                    return redirect(url_for('adminlist'))
            except sqlite3.Error as error:
                    print (f'{error}---->{error.__class__.__name__}')     
    except Exception as e:
        pass

@app.route('/insertadmininfo', methods=['GET','POST'])
def insertadmininfo():
    try:
        if request.method == 'GET':
            return render_template('admin_insert_admin_info.html')
        else:
            aname = request.form['aname']
            aphone = request.form['aphone']
            aemail = request.form['aemail']
            apwd = request.form['apwd']
            pwdchecker = passwordcheck(apwd)
            if pwdchecker:
                chpassword = changepass(apwd)
                try:
                    connection = get_connection()
                    cur = connection.cursor()
                    cur.execute("insert into admin (aname,aphone,aemail,apwd) values (?,?,?,?)", (aname,aphone,aemail,chpassword))
                    connection.commit()
                    flash('Inserted New Admin Info is Successful')
                    return redirect(url_for('adminlist'))
                except sqlite3.Error as error:
                    print(f'{error}----->{error.__class__.__name__}')
            else:
                flash('Password must be at least 8words with 1 uppercase, 1 digit, 1 special(eg.!@#$%)')
                a = True
                return render_template('admin_insert_admin_info.html', aname = aname, aphone = aphone, aemail = aemail, a = a)
    except Exception as e:
        pass

@app.route('/admindiseaselist', methods=['GET','POST'])
def admindiseaselist():
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("Select disid,disname from disease")
                diseaseinfo = cur.fetchall()
                return render_template('admindiseaselist.html', disinfo = diseaseinfo )
        # else:     
    except Exception as e:
        pass

@app.route('/admindiseaseinfo/<disease_name>:<disease_id>', methods=['GET','POST'])
def admindiseaseinfo(disease_name,disease_id):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select disdescription,dissymptoms,treatment from disease where disid='{disease_id}'")
                diseaseinfo = cur.fetchone()
                return render_template('admindiseaseinfo.html', disinfo = diseaseinfo, did = disease_id, name = disease_name )
        # else:     
    except Exception as e:
        pass

@app.route('/admininsertdiseaseinfo', methods=['GET','POST'])
def admininsertdiseaseinfo():
    try:
        if request.method == 'GET':
            return render_template('admin_insert_disease_info.html')
        else:
            diseasename = request.form['disease_name']
            diseasedes = request.form['disease_des']
            diseasesym = request.form['disease_sym']
            diseasetreat = request.form['disease_treat']
            adminId = session['aid']
            today = date.today()
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('insert into disease (disname,disdescription,dissymptoms,treatment,disdate,aid) values (?,?,?,?,?,?)',(diseasename,diseasedes,diseasesym,diseasetreat,today,adminId))
                conn.commit()
                return redirect(url_for('admindiseaselist'))
            except sqlite3.Error as error:
                flash('Failed to Insert! Try Again.')
                return render_template('admin_insert_disease_info.html')
            finally:
                if conn:
                    cur.close()
                    conn.close()
    except Exception as e:
        pass
    
@app.route('/adminupdatediseaseinfo:<did>', methods=['GET','POST'])
def adminupdatediseaseinfo(did):
    try:
        if request.method == 'GET':
            with get_connection() as con:
                cur = con.cursor()
                cur.execute(f"Select disname,disdescription,dissymptoms,treatment from disease where disid='{did}'")
                diseaseinfo = cur.fetchone()
            return render_template('admin_update_disease_info.html', disinfo = diseaseinfo, did = did)
        else:
            diseasename = request.form['disease_name']
            diseasedes = request.form['disease_des']
            diseasesym = request.form['disease_sym']
            diseasetreat = request.form['disease_treat']
            hdiseasedes = request.form['hdisease_des']
            hdiseasesym = request.form['hdisease_sym']
            hdiseasetreat = request.form['hdisease_treat']
            today = date.today()
            if diseasedes == '':
                diseasedes = hdiseasedes
            if diseasesym == '':
                diseasesym = hdiseasesym
            if diseasetreat == '':
                diseasetreat = hdiseasetreat
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(f"update disease set disname='{diseasename}', disdescription='{diseasedes}', dissymptoms='{diseasesym}', treatment='{diseasetreat}', disdate='{today}' where disid='{did}'")
                conn.commit()
                return redirect(f'/admindiseaseinfo/{diseasename}:{did}')
            except sqlite3.Error as error:
                flash('Failed to Update! Try Again.')
                return render_template('admin_update_disease_info.html')
            except TypeError as e:
                pass
            finally:
                if conn:
                    cur.close()
                    conn.close()
    except Exception as e:
        pass


@app.route('/admindiseasedel:<diid>', methods=['POST'])
def admindiseasedel(diid):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"delete from disease where disid='{diid}'")
        conn.commit()
        conn.close()
        flash('Deleting a disease information is successful.')
        return redirect(url_for('admindiseaselist'))
    except Exception as e:
        pass
    
@app.route('/adminbloginfo', methods=['GET','POST'])
def adminbloginfo():
    try:
        if request.method == 'GET':
            with get_connection() as connection:
                cur = connection.cursor()
                cur.execute("SELECT * FROM blog")
                database_data = cur.fetchall()
                cur.execute("SELECT pid,pname FROM patient")
                patients = cur.fetchall()
                cur.execute("SELECT did,dname FROM doctor")
                doctors = cur.fetchall()
                cur.execute("SELECT * FROM comment")
                comment = cur.fetchall()
                return render_template('adminpostinfo.html', blog_database = database_data, patients = patients, doctors = doctors, comments = comment)
        # else:     
    except Exception as e:
        pass

@app.route('/adminfeedbackinfo', methods=['GET','POST'])
def adminfeedbackinfo():
    try:
        if request.method == 'GET':
            with get_connection() as connection:
                cur = connection.cursor()
                cur.execute('SELECT * FROM feedback')
                database_data = cur.fetchall()
                cur.execute('SELECT pid,pname FROM patient')
                patients = cur.fetchall()
                cur.execute('SELECT did,dname FROM doctor')
                doctors = cur.fetchall()
                return render_template('adminfeedbackinfo.html', feedback_database = database_data, patients = patients, doctors = doctors)
        #else:
    except Exception as e:
        raise e
    
@app.route('/feedbackcheck:<fbid>', methods=['GET','POST'])
def feedbackcheck(fbid):
    try:
        aid = session['aid']
        with get_connection() as connection:
            cur = connection.cursor()
            cur.execute(f"update feedback set fbcheck='checked', aid={aid} where fbid={fbid}")
            connection.commit()
            flash('Checking Feedback is recorded!')
            return redirect('/adminfeedbackinfo')
    except Exception as e:
        raise e
@app.route('/feedbackdel:<fbid>', methods=['GET','POST'])
def feedbackdel(fbid):
    try:
        with get_connection() as connection:
            cur = connection.cursor()
            cur.execute(f"DELETE from feedback where fbid={fbid}")
            connection.commit()
            flash('Deleting feedback information is successful.')
            return redirect('/adminfeedbackinfo')
    except sqlite3.Error as error:
        print(f'{error}-->{error.__class__.__name__}')

@app.route('/termsandconds', methods=['GET','POST'])
def termsandconds():
    try:
        if request.method == 'GET':
            return render_template('termsandconditions.html')
        # else:     
    except Exception as e:
        pass

@app.route('/policy', methods=['GET','POST'])
def privancys():
    try:
        if request.method == 'GET':
            return render_template('privacyandpolicy.html')
        # else:     
    except Exception as e:
        pass



@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('aid', None)
    session.pop('did', None)
    session.pop('user', None)
    session.pop('pid', None)
    session.pop('image', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='localhost', port='5804', debug='True')                    
