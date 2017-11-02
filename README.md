# shiMaya_QuickBox

This is my personal Maya toolbox, including all the  useful mel and python tools.

and each category of functions are seperated into different mel/python files, like a modules system.


# shi_OneLineMaker.mel

Purpose

  * help you to convert multiple lines of mel code into 1 line
  * also help you to create the button creation code with give multiple lines of mel code

Screenshot

![mel_shi_onelinemaker_screenshot.png](screenshot/mel_shi_onelinemaker_screenshot.png?raw=true)


#  Scatter ======

  * A GUI python Maya tool to generate geometry instances at each particle position with optional random rotation and scale.

**Features**
  * v3.0 (2016.08.10)
    - support random geo from geo list
    - support both vtx and particle based position spread
    - add random shortlist vtx feature
    - independent x,y,z scale random option
    - align to normal on surface option
    - open option for distance filter option
    - open option for duplicate as instance for geo input
    - add scale min, so range from min to scale
  * v2.0
    * scatter with defined geometry and defined/auto defined particle system
    * scatter with optional random rotation/scale at individually x,y,z axis
    * each individual scale can have same value on all axis, maintain its proportion
    * super cool feature: it has object distance detection built-in, if particle distance is smaller than the bounding box diagonal distance, the object won't duplicate at that spot

**Usage**
  - Select the geo/s to scatter;
  - select particle/vtx for the position info,
    - for particle, optionally select the surface to create a object emit particle, then play timeline to a frame that fit your partcile amount.
    - for vtx, optionally random pickup a num of points from your vtx selection
  - use scatter random option (TRS,align,mixDistBetPoint,Inst);
  - scatter button to scatter.
  
 ![scatter_v3.5_screenshot.png](screenshot/scatter_v3.5_screenshot.png?raw=true)
