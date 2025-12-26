from cmu_graphics import *
import math

'''
Features:

Text Boxes to Change Field:
Click text boxes to enter in a polynomial. The user must use spaces between terms,
each term can only have one variable (e.g. xy will not work), and all numbers must
be integers. To lock in the polynomial you want for each component, press enter. 
If you click elsewhere before clicking elsewhere, the textbox will clear. The 
current field will update after the user clicks enter.

Changing the View of the Graph:
The third button will either say graph mode or vector mode. When graph mode is on,
the button will be labeled vector mode and vice versa. Graph mode shows a standard
grid view and vector mode shows the vector at each point.

Adjusting Axes:
To adjust the bounds of each axis, click the button that corresponds to the axis
you want to adjust, then click the up or down arrow keys. The numbers at the end
of the graph will show what the current bounds of the graph are.

Toggling Particle:
The user can use the 'n' and 'p' keys to change the particle from positive to
negative. Positive particles will move with the arrows whereas negative arrows 
will move against the arrows.

Pause Button:
Clicking the pause button will pause the motion of any particles that are currently
on the graph.


Clear Button:
Clicking this button will reset the axes, the field back to 0,0, the mode back
to graph mode, and delete all particles


Grading Shortcuts:
a: Enters the field <y, x>
b: Enters the field <y + 2, x + y>
c: Enters the field <x^2 + 1, y^2 + 1>
'''

class Arrow:
    def __init__(self, size, x, y, dx, dy):
        self.size = size
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        
    def drawArrow(self):
        if self.dx == 0 and self.dy == 0:
            return
        elif self.dx == 0 and self.dy > 0:
            angle = math.pi/2
        elif self.dx == 0 and self.dy < 0:
            angle = 3*math.pi/2
        #if dx is negative add pi to the angle
        else:
            if self.dx < 0:
                angle = math.atan(self.dy/self.dx) + math.pi
            else:
                angle = math.atan(self.dy/self.dx)
        drawPolygon(self.x + self.size*math.cos(angle), self.y + self.size*math.sin(angle), 
                    self.x + self.size*0.5*math.cos(angle + math.pi/2), self.y + self.size*0.5*math.sin(angle + math.pi/2),
                    self.x + self.size*0.5*math.cos(angle - math.pi/2), self.y + self.size*0.5*math.sin(angle - math.pi/2),
                    fill = 'black')
        

class TextBox:
    def __init__(self, x, y, width, height):
        self.text = ''
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = None
        self.selected = False
        
    def inBox(self, mx, my):
        return (self.x<= mx <= self.x+self.width and 
            self.y<=my<= self.y+self.height)
            
    def drawTextBox(self):
        if self.selected:
            fill = 'grey'
            
        else:
            fill = None
        drawRect(self.x, self.y, self.width, self.height, border = 'black', fill = fill)
        drawLabel(self.text, self.x + self.width/2, self.y + self.height/2, size = 15)
        
    
    
class Button:
    def __init__(self, text, x, y, width, height, fill):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = fill
        
    def hoverButton(self, mx, my):
        if (self.x<= mx <= self.x+self.width and 
            self.y<=my<= self.y+self.height):
            self.fill = 'grey'
            
        else:
            self.fill = None
        
    def drawButton(self):
        drawRect(self.x, self.y, self.width, self.height, border = 'black', fill = self.fill)
        drawLabel(self.text, self.x + self.width/2, self.y + self.height/2, size = 15)
        
    def clickButton(self, mx, my):
        return (self.x<= mx <= self.x+self.width and 
            self.y<=my<= self.y+self.height)
                
    

class Particle:
    def __init__(self, cx, cy, radius, color, field, rows, cols, boardLeft, boardTop, boardWidth, boardHeight, charge):
        self.color = color
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.field = field
        self.rows = rows
        self.cols = cols
        self.boardLeft = boardLeft
        self.boardTop = boardTop
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight
        self.charge = charge

    
    def getGraphX(self):
        return (self.cx - (self.boardLeft + self.boardWidth/2))/(self.boardWidth/self.cols)
        
    def getGraphY(self):
        return -1*(self.cy - (self.boardTop + self.boardHeight/2))/(self.boardHeight/self.rows)
    
    def getDx(self):
        graphX = self.getGraphX()
        graphY = self.getGraphY()
        return evalPolynomial(self.field.xCompStr, graphX, graphY)
        
        
    def getDy(self):
        graphX = self.getGraphX()
        graphY = self.getGraphY()
        return evalPolynomial(self.field.yCompStr, graphX, graphY)
        
        
    def drawParticle(self):
        drawCircle(self.cx, self.cy, self.radius, fill = self.color)
        


class VectorField:
    def __init__(self, xCompStr, yCompStr):
        self.xCompStr = xCompStr
        self.yCompStr = yCompStr
        
    def __repr__(self):
        return f'<{self.xConstant}{self.xVar}^{self.xExp}, {self.yConstant}{self.yVar}^{self.yExp}>'
        
 

def evalTerm(term, x, y):
    for c in term:
        if 'x' not in term and 'y' not in term: 
            return int(term)
        elif 'x^' in term:
            if term.startswith('x^'):
                exponent = term[2:]
                return x ** int(exponent)
            constant, exponent = term.split('x^')
            return int(constant) * (x**int(exponent))
        elif 'y^' in term:
            if term.startswith('y^'):
                exponent = term[2:]
                return y ** int(exponent)
            constant, exponent = term.split('y^')
            return int(constant) * (y**int(exponent))
        else:
            constant = term[:-1]
            if constant == "":
                constant = 1
            variable = term[-1]
            if variable == 'x':
                return int(constant) * x
            elif variable == 'y':
                return int(constant) * y
            
            
    

def evalPolynomial(p, x, y):
    if p == '':
        return 0
    result = 0
    sign = 1
    for part in p.split():
        if part =='+':
            sign = 1
        elif part == '-':
            sign = -1
        else:
            thisTerm = evalTerm(part, x, y)
            result += sign * thisTerm
        
    return result


def onAppStart(app):
        app.boardLeft = 50
        app.boardTop = 150
        app.boardWidth = 300
        app.boardHeight = 300
        app.stepsPerSecond = 50
        resetApp(app)
        
        
def resetApp(app):
    app.rows = 20
    app.cols = 20
    app.graph = True
    app.paused = False
    app.particles = []
    app.nextParticleColor = 'red'
    app.nextParticleR = 7
    app.nextParticleCharge = '+'
    app.selected = False
    app.field = VectorField('0', '0')
    app.pauseButton = Button('Pause', 400, 280, 150, 30, None)
    app.clearButton = Button('Clear', 400, 325, 150, 30, None)
    app.modeButton = Button('Vector Mode', 400, 370, 150, 30, None)
    app.xAxisButton = Button('X-Axis', 400, 415, 70, 30, None)
    app.xAxisSelected = False
    app.yAxisButton = Button('Y-Axis', 480, 415, 70, 30, None)
    app.yAxisSelected = False
    app.xTextBox = TextBox(100, 50, 90, 20)
    app.yTextBox = TextBox(210, 50, 90, 20)


    
def drawArrow(app, left, top, width, height, row, col):
    graphX = row - 10
    graphY = col - 10
    x = left
    y = top
    #component will be potential dy and potential dx
    #treating each box as 10
    dot = Particle(x, y, 3, 'black', app.field, app.rows, app.cols, app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, 'x')
    dx = dot.getDx()/5
    dy = dot.getDy()/5
    dot.drawParticle()
    drawLine(x, y, x+(dx*app.boardWidth/app.cols), y-(dy*app.boardHeight/app.rows),  lineWidth = 2)
    arrow = Arrow(10, x+(dx*app.boardWidth/app.cols), y-(dy*app.boardHeight/app.rows), dx, -1*dy)
    arrow.drawArrow()
    
def drawBoard(app):
    if app.graph:
        for row in range(app.rows):
            for col in range(app.cols):
                drawCell(app, row, col)
    else:
        for row in range(1, app.rows, 3):
            for col in range(1, app.cols, 3):
                drawCell(app, row, col)

def drawCell(app, row, col):
    cellTop, cellLeft = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellWidthHeight(app)
    if app.graph:
        drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = None, border = 'black', borderWidth = 0.5)
    #draw arrows inside the middle of the box
    else:
        drawArrow(app, cellLeft, cellTop, cellWidth, cellHeight, row, col)
    
def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellWidthHeight(app)
    cellTop = app.boardTop + row*cellHeight
    cellLeft = app.boardLeft + col*cellWidth
    return cellTop, cellLeft
    
def getCellWidthHeight(app):
    cellWidth = (app.boardWidth)/app.cols
    cellHeight = (app.boardHeight)/app.rows
    return cellWidth, cellHeight

def drawNextParticle(app):
    drawCircle(475, 240, app.nextParticleR, fill = app.nextParticleColor)
    drawLabel(app.nextParticleCharge, 475, 240, fill = 'white', size = 20)
    

def getCompStr(constant, variable, exponent):
    if constant == 0:
        return '0'
        
    if variable == '' or exponent == 0:
        return str(constant)
        
        
    if constant == 1:
        if exponent == 1:
            return str(variable)
        return f'{variable}^{exponent}'
    
    if exponent == 1:
        return f'{constant}{variable}'
        
    return f'{constant}{variable}^{exponent}'

def redrawAll(app):
    #display current field
    drawLabel(f'Current Field: <{app.field.xCompStr}, {app.field.yCompStr}>', 200, 90, size = 20)
    #title and graph
    drawBoard(app)
    drawLabel('Vector Field Simulator', app.width/2, 20, size = 30)
    drawLine(app.boardLeft-30, app.boardTop + app.boardHeight/2, app.boardLeft + app.boardWidth + 30,  
    app.boardTop + app.boardHeight/2, arrowStart = True, arrowEnd = True, lineWidth = 3)
    drawLine(app.boardLeft + app.boardWidth/2, app.boardTop-30, 
    app.boardLeft + app.boardWidth/2, app.boardTop + app.boardHeight+30, arrowStart = True, arrowEnd = True, lineWidth = 3)
    #draw text boxes
    app.xTextBox.drawTextBox()
    app.yTextBox.drawTextBox()
    #pause button
    if not app.paused:
        app.pauseButton.text = 'Pause'
    else:
        app.pauseButton.text = 'Play'
    app.pauseButton.drawButton()
    #clear button
    app.clearButton.drawButton()
    #graph mode or vector mode button
    if app.graph:
        app.modeButton.text = "Vector Mode"
    else:
        app.modeButton.text = "Graph Mode"
    app.modeButton.drawButton()
    
    #draw axis buttons
    app.xAxisButton.drawButton()
    app.yAxisButton.drawButton()
    drawLabel(str(app.cols//2), 370, 280)
    drawLabel('-' + str(app.cols//2), 30, 280)
    drawLabel(str(app.rows//2), 200, 110)
    drawLabel('-' + str(app.rows//2), 200, 490)
    drawLabel('Use the up and down arrows', 475, 460)
    drawLabel('to adjust the axes', 475, 480)
    #newparticle
    drawNextParticle(app)
    drawLabel('Next Particle', 475, 145, bold = True)
    drawLabel('Toggle charge with', 475, 170)
    drawLabel('p (positive),', 475, 185)
    drawLabel('n (negative)', 475, 200)
    drawRect(400, 130, 150, 135, fill = None, border = 'black')
    #particles
    for particle in app.particles:
        drawCircle(particle.cx, particle.cy, particle.radius, fill = particle.color)
        drawLabel(particle.charge, particle.cx, particle.cy, fill = 'white', size = 20)

def onKeyPress(app, key):
    #text box mechanics
    if app.yTextBox.selected == True and (key.isdigit() or key == '+' or key == '-' or key == '^' or key == 'x' or key == 'y' or key == 'space'):
        if key == 'space':
            app.yTextBox.text += ' '
        else:
            app.yTextBox.text += key
    elif app.xTextBox.selected == True and (key.isdigit() or key == '+' or key == '-' or key == '^' or key == 'x' or key == 'y' or key == 'space'):
        if key == 'space':
            app.xTextBox.text += ' '
        else:
            app.xTextBox.text += key
        
    #update vector string
    if app.yTextBox.selected == True and key == 'enter':
        app.yCompStr = app.yTextBox.text
        app.field.yCompStr = app.yTextBox.text
    if app.xTextBox.selected == True and key == 'enter':
        app.xCompStr = app.xTextBox.text
        app.field.xCompStr = app.xTextBox.text
        
        
    if key == 'c':
        print(app.field.xCompStr, app.field.yCompStr)
        for particle in app.particles:
            print(particle.getGraphX(), particle.getGraphY(), particle.getDx(), particle.getDy())
        
    if key == 'n':
        app.nextParticleColor = 'blue'
        app.nextParticleCharge = '-'
    elif key == 'p':
        app.nextParticleColor = 'red'
        app.nextParticleCharge = '+'
        
    if key == 'up':
        if app.xAxisSelected:
            app.cols += 2
        if app.yAxisSelected:
            app.rows += 2
    elif key == 'down':
        if app.xAxisSelected:
            app.cols -= 2
        if app.yAxisSelected:
            app.rows -= 2
            
    #grading shortcuts
    #can take in variables
    if key == 'a':
        app.field.xCompStr = 'y'
        app.field.yCompStr = 'x'
        
    #can take in polynomials
    elif key == 'b':
        app.field.xCompStr = 'y + 2'
        app.field.yCompStr = 'x + y'
        
    #can raise powers
    elif key == 'c':
        app.field.xCompStr = 'x^2 + 1'
        app.field.yCompStr = 'y^2 + 1'
        
        

def distance(x0, y0, x1, y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5

def onMouseMove(app, mouseX, mouseY):
    app.clearButton.hoverButton(mouseX, mouseY)
    app.pauseButton.hoverButton(mouseX, mouseY)
    app.modeButton.hoverButton(mouseX, mouseY)

#append to new particles
def onMousePress(app, mouseX, mouseY):
    #if press next particle allow to drag into graph
    if distance(mouseX, mouseY, 475, 240) <= app.nextParticleR:
        app.selected = True
        app.particles.append(Particle(mouseX, mouseY, app.nextParticleR, app.nextParticleColor, app.field, app.rows, app.cols, app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, app.nextParticleCharge))
        app.nextParticleColor = 'red'
        app.nextParticleR = 7
        app.nextParticleCharge = '+'
    #if click in textBox
    if app.xTextBox.inBox(mouseX, mouseY):
        app.xTextBox.selected = True
        app.yTextBox.selected = False
        app.yTextBox.text = ''
    elif app.yTextBox.inBox(mouseX, mouseY):
        app.yTextBox.selected = True
        app.xTextBox.selected = False
        app.xTextBox.text = ''
    else:
        app.yTextBox.selected = False
        app.xTextBox.selected = False
        app.yTextBox.text = ''
        app.xTextBox.text = ''
    #click on pause
    if app.pauseButton.clickButton(mouseX, mouseY):
        if app.paused:
            app.paused = False
        else:
            app.paused = True
    #click on clear
    if app.clearButton.clickButton(mouseX, mouseY):
        resetApp(app)
    #click on mode button
    if app.modeButton.clickButton(mouseX, mouseY):
        if app.graph:
            app.graph = False
        else:
            app.graph = True
            
    if app.xAxisButton.clickButton(mouseX, mouseY):
        app.yAxisSelected = False
        app.yAxisButton.fill = None
        if app.xAxisSelected:
            app.xAxisSelected = False
            app.xAxisButton.fill = None
        else:
            app.xAxisSelected = True
            app.xAxisButton.fill = 'grey'
    elif app.yAxisButton.clickButton(mouseX, mouseY):
        app.xAxisSelected = False
        app.xAxisButton.fill = None
        if app.yAxisSelected:
            app.yAxisSelected = False
            app.yAxisButton.fill = None
        else:
            app.yAxisSelected = True
            app.yAxisButton.fill = 'grey'
    
   

#update location of particle when dragged
def onMouseDrag(app, mouseX, mouseY):
    if app.selected:
        particle = app.particles[-1]
        particle.cx = mouseX
        particle.cy = mouseY
        
def onMouseRelease(app, mouseX, mouseY):
    #make sure dropped particle is on graph
    if app.selected:
        if not (app.boardLeft <= mouseX + app.particles[-1].radius and 
        mouseX - app.particles[-1].radius <= app.boardLeft + app.boardWidth and 
        app.boardTop <= mouseY + app.particles[-1].radius and
        mouseY - app.particles[-1].radius <= app.boardTop + app.boardHeight):
            app.particles.pop(-1)
        app.selected = False

def onStep(app):
    if not app.paused:
        i = 0
        while i < len(app.particles):
            particle = app.particles[i]
            #print(particle.getGraphX(), particle.getGraphY(), particle.getDx(), particle.getDy())
            if particle.charge == '+':
                particle.cx += particle.getDx()/5
                particle.cy -= particle.getDy()/5
            elif particle.charge == '-':
                particle.cx -= particle.getDx()/5
                particle.cy += particle.getDy()/5
            
            
            #if particle is out of graph, pop
            if app.selected == False:
                if not (app.boardLeft <= particle.cx + app.particles[i].radius and 
                particle.cx - app.particles[i].radius <= app.boardLeft + app.boardWidth and 
                app.boardTop <= particle.cy + app.particles[i].radius and
                particle.cy - app.particles[i].radius <= app.boardTop + app.boardHeight):
                    app.particles.pop(i)
                    i -= 1
            i += 1
            

    
def main():
    runApp()
    

main()




