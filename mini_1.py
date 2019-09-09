from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
import time
from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input,decode_predictions
from keras.preprocessing.image import image
import os
import threading
import numpy as np
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import pickle 
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
import re
from kivy.uix.popup import Popup


class MyGrid(ScreenManager):
    

    dir_list = './dict_file.txt'
    model_file = './model_file'


    def __init__(self,**kwargs):
        super(MyGrid,self).__init__(**kwargs)
       
        self.thread = threading.Thread(target = self.pressed)

        self.path = []
        self.path.append('C:\\Users\CLIVE\Downloads')
        self.path_list = []
        self.input_list = []


        ################# creating a popup layout #####################

        box = BoxLayout()

        box.add_widget(Label(text = 'Model Processing Please Wait.....'))


        self.wait_dialog = Popup(title = 'Wait Please..',content = box,size_hint = (0.5,0.5))


        #check for saved paths 


        if os.path.exists(MyGrid.dir_list):
            with open(MyGrid.dir_list,'r') as f:
                r = f.readlines()

            for i in r:
                self.path.append(re.sub('\\n','',i))        




        for p in self.path:

            self.path_list.append([i for i in os.listdir(p) if i.split('.')[-1].lower() in ['png','jpg','jpeg']])

        # self.path_list = [[i for i in os.listdir('C:\\Users\CLIVE\Downloads') if i.split('.')[-1].lower() in ['png','jpg','jpeg']]]
        

        for i in self.path:
    
            for j in os.listdir(i):
                if j.split('.')[-1].lower() in ['png','jpg','jpeg']:

                    self.input_list.append(os.path.join(i,j))    



              
        self.model  = InceptionV3(include_top = True,weights = 'imagenet',input_shape = (299,299,3))
        
      

    
        self.screen1  = Screen(name = 'screen1')
        self.screen2 = Screen(name = 'screen2')


        # define screen 2

        self.screen2_layout = RelativeLayout()

        self.back = Button(text ="<-BACK",size_hint = (0.2,0.1),pos_hint = {'x':0,'top':1})


        self.back.bind(on_press = self.move_back)

        self.grid2  = GridLayout(size_hint = (1,1),pos_hint = {'x':0,'top':0.9})
        
        self.grid2.cols = 4

        self.screen2_layout.add_widget(self.back)
        self.screen2_layout.add_widget(self.grid2)


        self.screen2.add_widget(self.screen2_layout)





        
        
        #define layout for screen 1   
            
        self.screen1_layout = RelativeLayout()    


        self.inputpaths = TextInput(text = 'Enter new path here ',size_hint= (0.6,0.1),pos_hint = {'x':0,'top':1})
        self.set = Button(text = 'Set',size_hint = (0.2,0.1),pos_hint ={'right':0.8,'top':0.998})
        self.save = Button(text = 'Save',size_hint = (0.2,0.1),pos_hint ={'right':1,'top':0.998})

        self.text1 = TextInput(text = 'Enter name',size_hint= (0.8,0.1),pos_hint = {'x':0,'top':0.9})
        self.button1 = Button(text = 'Search',size_hint = (0.2,0.1),pos_hint ={'right':1,'top':0.9})
       
        scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height),pos_hint = {'x':0,'top':0.8})

        # self.image =  Image(source = os.path.join(self.path[0],self.path_list[0][1]),size_hint = (0.5,0.5),pos_hint = {'center_x':0.5,'center_y':0.5})
        
 
        self.grid  = GridLayout(size_hint_y = None,spacing = 10)
        self.grid.cols = 4
      


        for i,j in zip(self.path,self.path_list):
            
            for k in j:
                self.image = Image(source = os.path.join(i,k),size_hint_y = None,size = (200,200))
                self.grid.add_widget(self.image)
        

        self.grid.bind(minimum_height=self.grid.setter('height'))
        

        self.button1.bind(on_press = self.pressed)
        self.set.bind(on_press = self.pathloader)
        self.save.bind(on_press = self.save_dict)


        scroll.add_widget(self.grid)

        self.screen1_layout.add_widget(scroll)
        self.screen1_layout.add_widget(self.inputpaths)
        self.screen1_layout.add_widget(self.set)
        self.screen1_layout.add_widget(self.button1)
        self.screen1_layout.add_widget(self.save)
        self.screen1_layout.add_widget(self.text1)


        self.screen1.add_widget(self.screen1_layout)

        self.add_widget(self.screen1)
        self.add_widget(self.screen2)

        
    def save_dict(self,instance):
        
        if len(self.path) > 1:

           with open(MyGrid.dir_list,'w') as f:
               f.write(self.path[-1]+'\n')  


    def pathloader(self,instance):

        print(self.inputpaths.text)

        if os.path.exists(self.inputpaths.text):
            self.path.append(self.inputpaths.text)
            # self.input_list.append(os.path.join(self.path[-1],k))   
            self.path_list.append([i for i in os.listdir(self.path[-1]) if i.split('.')[-1].lower() in ['png','jpg','jpeg']])


            self.grid.clear_widgets()

            for i,j in zip(self.path,self.path_list):
                
                for k in j:
                    
                    
                     
                    self.image = Image(source = os.path.join(i,k),size_hint_y = None,size = (200,200))
                    self.grid.add_widget(self.image)

        
            for i in self.path_list[-1]:
                self.input_list.append(os.path.join(self.path[-1],i))


    def get_ops(self):
        images = []
        ops = []

        for i,j in zip(self.path,self.path_list):
                
                for k in j:
                    img = image.load_img(os.path.join(i,k), target_size=(299, 299))
                    x = image.img_to_array(img)
                    #x = np.expand_dims(x, axis = 0)
                    x = preprocess_input(x)
                
                    images.append(x)
        print('get_images',np.array(images).shape)        
        features = self.model.predict(np.array(images))
        ops.append(np.squeeze(np.array(decode_predictions(features, top = 1))))
        



        return ops
    
    def initial(self,instance):
        threading.Thread(target= self.pressed).start()

    def pressed(self,instance):


        # self.wait_dialog.open()

        search = self.text1



        images = np.array(self.get_ops())
        ops =  []



        for i in images:

            for j in i:
                ops.append(j)

        print('len of ops',len(ops))
        print('len of images',len(self.input_list))
        
        # features = self.model.predict(np.array(images))
        # op = np.squeeze(np.array(decode_predictions(features, top = 1)))
        
        # print('imageshape',images.shape)



        
       
        self.grid2.clear_widgets()
        self.current = 'screen2'

        
        
        
        for j,i in enumerate(ops):
        
    
            if search.text in i[1].replace('_',' '):
                # plt.figure()
                # plt.imshow(cv2.imread(os.path.join(path,lt[j])))
                print(i,self.input_list[j])
                # self.image.source = os.path.join(self.path,self.path_list[j])


                self.image = Image(source = os.path.join(self.input_list[j]),size_hint = (0.5,0.5),pos = (0+j*10,0+j*10))
                self.grid2.add_widget(self.image)


        print('image searched',search.text)
        # print(self.model)

        # self.wait_dialog.dismiss()


    def move_back(self,instance):
        self.current = 'screen1'


       
        

        
        
    

class MyApp(App):
    
     

    def build(self):
        
        return MyGrid()


    
    
     

 

a = MyApp()



a.run()
