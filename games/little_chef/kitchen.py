"""Flat kitchen illustration. Shapes are editable; no external artwork required."""
import cv2
import numpy as np

CREAM=(226,242,249); PAPER=(238,248,252); INK=(64,86,92)
SAGE=(151,176,162); OLIVE=(106,139,123); WOOD=(112,170,211)

def rounded(c,a,b,color,r=12):
    x,y=a; xx,yy=b; r=min(r,(xx-x)//2,(yy-y)//2)
    cv2.rectangle(c,(x+r,y),(xx-r,yy),color,-1)
    cv2.rectangle(c,(x,y+r),(xx,yy-r),color,-1)
    for p in ((x+r,y+r),(xx-r,y+r),(x+r,yy-r),(xx-r,yy-r)):cv2.circle(c,p,r,color,-1,cv2.LINE_AA)

def kitchen():
    c=np.full((640,960,3),CREAM,np.uint8)
    # Sideboard, dish cabinet and window; flat overlapping color fields only.
    cv2.rectangle(c,(0,82),(960,382),PAPER,-1)
    for y in (120,180,240,300,360):cv2.line(c,(0,y),(960,y),(215,233,239),1)
    rounded(c,(752,92),(941,253),SAGE,18)
    rounded(c,(766,103),(927,240),(208,224,218),8)
    cv2.rectangle(c,(844,103),(850,240),SAGE,-1)
    for y in (155,206):cv2.rectangle(c,(766,y),(927,y+6),SAGE,-1)
    for x in (786,807,828):
        cv2.ellipse(c,(x,134),(8,19),0,0,360,CREAM,-1,cv2.LINE_AA)
    for y in (184,224):
        for x in (790,892):
            cv2.ellipse(c,(x,y),(21,8),0,0,180,WOOD,-1,cv2.LINE_AA)
            cv2.ellipse(c,(x,y-2),(21,4),0,0,360,CREAM,-1,cv2.LINE_AA)
    # Small sink and curved faucet next to the serving space.
    cv2.rectangle(c,(745,272),(960,365),WOOD,-1)
    rounded(c,(778,291),(932,344),CREAM,16)
    rounded(c,(790,301),(920,335),OLIVE,12)
    cv2.ellipse(c,(857,281),(19,24),0,180,360,OLIVE,7,cv2.LINE_AA)
    cv2.line(c,(838,282),(838,304),OLIVE,7,cv2.LINE_AA)
    cv2.rectangle(c,(752,351),(960,414),SAGE,-1)
    cv2.line(c,(853,354),(853,413),OLIVE,2)
    rounded(c,(827,369),(842,374),CREAM,2);rounded(c,(866,369),(881,374),CREAM,2)
    # Food display counter and clean foreground preparation surface.
    rounded(c,(16,182),(738,378),(131,186,221),16)
    cv2.rectangle(c,(18,379),(738,408),SAGE,-1)
    for x in (195,374,553):cv2.line(c,(x,383),(x,407),OLIVE,2)
    rounded(c,(16,400),(944,560),(185,218,237),20)
    cv2.rectangle(c,(0,563),(960,640),PAPER,-1)
    return c
