import os, sys, cgi, glob
from PIL import Image, ImageFont, ImageDraw

class TextAnimation:

	def __init__(self, inputFile, textAnimationSize):
		self.inputFile = os.path.abspath(inputFile)
		textAnimationSize = textAnimationSize.split('*')
		self.textAnimationSize = (int(textAnimationSize[0]), int(textAnimationSize[1]))
		self.font = ImageFont.truetype('simsun.ttc', 14)
		self.sourceChars = self.genSourceChars((32, 126))

	def genSourceChars(self, asciiRange):
		sourceChars = list()
		for code in range(asciiRange[0], asciiRange[1]):
			sourceChars.append(chr(code))
		return sourceChars

	def getMaxFontSize(self):
		charsSize = list()
		for char in self.sourceChars:
			charsSize.append(self.font.getsize(char))
		maxFontSize = reduce(lambda x, y: (max(x[0], y[0]), max(x[1], y[1])), charsSize)
		return maxFontSize

	def calCharPixel(self):
		charsGrayScale = dict()
		canvasSize = self.getMaxFontSize()
		totalPixel = canvasSize[0]*canvasSize[1]
		forCalIm = Image.new('L', canvasSize, 'white')
		drawForCalIm = ImageDraw.Draw(forCalIm)
		for char in self.sourceChars:
			drawForCalIm.rectangle([(0, 0), canvasSize], fill='white')
			drawForCalIm.text((0, 0), char, font=self.font)
			charGrayScale = forCalIm.getcolors()
			charsGrayScale.update({char: (255-(reduce(lambda x, y: (totalPixel, x[1]+y[1]), charGrayScale)[1]/totalPixel))})
		return charsGrayScale

	def textStruct(self, imagePointer):
		resultText = ''
		charsGrayScale = self.calCharPixel()
		imagePointer = imagePointer.resize((self.textAnimationSize[0], self.textAnimationSize[1]*2))
		imagePointer = imagePointer.convert('L')
		for row in range(self.textAnimationSize[1]):
			for col in range(self.textAnimationSize[0]):
				pixel = imagePointer.getpixel((col, row*2))
				char = min(charsGrayScale.iterkeys(), key=lambda k: abs(pixel-charsGrayScale[k]))
				resultText += char
			resultText += '\n'
		return resultText

	def writeHtml(self, resultText):
		fp = open('TA.html', 'w')
		htmlHead = \
		'''
		<html>
		<head>
		<style>
		pre{display:none;font-family:simsun;font-size:14px;line-height:14px;}
		</style>
		<script>
		window.onload = function() {
			var pres = document.getElementsByTagName('pre');
			var i = 0;
			var play = function() {
				if (i > 0) {
					pres[i-1].style.display = 'none';
				}
				pres[i].style.display = 'block';
				i++;
				if (i == pres.length) {
					clearInterval(run)
				}
			}
			run = setInterval(play, 33)
		}
		</script>
		</head>
		<body>
		'''
		htmlFoot = \
		'''
		</body>
		</html>
		'''
		fp.write(htmlHead)
		for text in resultText:
			fp.write('<pre>')
			fp.write(cgi.escape(text, quote=True))
			fp.write('</pre>')
		fp.write(htmlFoot)
		fp.close()

	def convert(self):
		resultText = list()

		if os.path.isfile(self.inputFile):
			try:
				im = Image.open(self.inputFile)
			except Exception as e:
				im = None
				print e
			if not im == None:
				resultText.append(self.textStruct(im))

		elif not os.path.isdir(self.inputFile):
			print 'Invalid directory.'
			return

		else:
			filePaths = glob.glob(self.inputFile + '/*.bmp')
			filePaths = sorted(filePaths, key=os.path.getmtime)
			for path in filePaths:
				try:
					im = Image.open(path)
				except Exception as e:
					im = None
					print e
				if not im == None:
					resultText.append(self.textStruct(im))
					print path + '[Complete]'
		self.writeHtml(resultText)

def instrct():
	print '2 arguments required to run this program.'
	print 'first for input file,'
	print 'second for text animation size.'

def main():
	if not len(sys.argv) == 3:
		instruct()

	inputFile = sys.argv[1]
	textAnimationSize = sys.argv[2]
	
	TA = TextAnimation(inputFile, textAnimationSize)
	TA.convert()

if __name__ == '__main__':
	main()