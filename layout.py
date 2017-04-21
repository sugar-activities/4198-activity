''' Overall Frontend Layout'''
class Colors:
	grey 	= '#efefef'
	green 	= '#75b844'
	lime 	= '#cef474'
	yellow 	= '#ffff33'
	blue 	= '#94b0b4'
	black 	= '#000000'
	white	= '#ffffff'

class TextFormat:
	color = Colors().white
	size = 36
	background = None
	def __init__(self, color=None, size=None, background=None):
		if color != None: self.color = color
		if size != None: self.size = size
		if background != None: self.background = background
		

class Layout:
	user_name = "chris"
	port = 50123
	
	background = Colors().black;
	
	class Question:
		x = 20
		y = 20
		width = 860
		height = 650
		border = '3px ' + Colors().green;
		background = Colors().black;
		class Text:
			x = 20
			y = 12
			size = 46
			color = Colors().green;
		class Image:
			x = 10
			y = 60
		
	class MenuTop:
		x = 900
		y = 20
		width = 280
		height = 50
		border = '2px ' + Colors().blue
		class Text:
			x = 20
			y = 10
			size = 46
			color = Colors().green
			text = 'Menu'
			
	class MenuMain:
		x = 900
		y = 80
		width = 280
		height = 590
		border = '2px '  + Colors().blue
		background = Colors().black
		class Button:
			x = 9
			y = 10
			width = 260
			height = 40
			border = '2px ' +  Colors().green
			background = Colors().black
			class Text:
				x = 20
				y = 12
				size = 30
				color =  Colors().green;
			class Button_Directory:
				border = '2px ' +  Colors().blue
				background = Colors().black
				class Text:
					size = 30
					color =  Colors().green
				
	class Toolbar:
		x = 20
		y = 690
		width = 1160
		height = 100
		border = '2px '  + Colors().blue;
		background = Colors().black;
		class Text:
			size = 26
			color =  Colors().white;

		class FoundLine:
			x = 30
			y = 18
			width = 400
			height = 24	
			padding = 4
			image = "images/Emotes/face-grin_24px.png"
			image_width = 34
			image_left = 0
			class Outside:
				border = "1px " + Colors().blue
				background = Colors().black
			class Inside:
				border = "0px " + Colors().blue
				background = Colors().green
		class NotFoundLine:
			x = 30
			y = 52
			width = 400
			height = 24	
			padding = 4
			image = "images/Emotes/face-devil-grin_24px.png"
			image_width = 34
			image_left = 2
			class Outside:
				border = "1px " + Colors().blue
				background = Colors().black
			class Inside:
				border = "0px " + Colors().blue
				background = Colors().blue
		
	class Polygon:
		color =  Colors().yellow;
		
	class TextInput:
		class Box:
			x = 350
			y = 140
			width = 340
			height = 36
			background = Colors().black
			border = '2px ' + Colors().white
		class Text:
			size = 36
			color = Colors().white


	class QuestionEntry:
		class Box:
			background = Colors().black
			border = '2px ' + Colors().white
		class Text:
			size = 30
			color = Colors().white