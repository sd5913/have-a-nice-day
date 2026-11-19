"""Shared input test only; does not import any member's mini-game."""
import argparse
from pathlib import Path
import cv2
import numpy as np
from utils.hand_input import InputFilter
from utils.game_controls import DragObject

def run():
    parser=argparse.ArgumentParser();parser.add_argument('--camera',type=int,default=0)
    args=parser.parse_args()
    w,h=960,640; window='Shared input test'
    cv2.namedWindow(window)
    mouse={'x':.3,'y':.5,'down':False,'inside':True}
    def event(kind,x,y,flags,param):
        mouse.update(x=x/w,y=y/h,inside=0<=x<w and 0<=y<h)
        if kind==cv2.EVENT_LBUTTONDOWN:mouse['down']=True
        if kind==cv2.EVENT_LBUTTONUP:mouse['down']=False
    cv2.setMouseCallback(window,event)
    source='mouse';tracker=cap=None;error='';f=InputFilter(1);obj=DragObject(.3,.5)
    try:
        while True:
            frame=None
            if source=='hand':
                ok,frame=cap.read()
                hand=tracker.update(cv2.flip(frame,1)) if ok else tracker.processor.filter.update(tracked=False)
            else:hand=f.update(mouse['x'],mouse['y'],mouse['down'],tracked=mouse['inside'],source='mouse')
            result=obj.update(hand)
            c=np.full((h,w,3),245,dtype=np.uint8)
            status=('Open hand / release once' if not hand.ready else ('Pinched' if hand.pinched else 'Ready')) if hand.tracked else 'No hand - paused'
            lines=['SHARED HAND INPUT', 'H webcam / M mouse / Q quit',source.upper()+' | '+status,
                   'Drag the orange circle. Losing tracking cancels, not drops.',
                   'Event: '+str(result),error[:110]]
            for i,line in enumerate(lines):cv2.putText(c,line,(25,35+i*32),cv2.FONT_HERSHEY_SIMPLEX,.6,(60,60,60),1,cv2.LINE_AA)
            cv2.circle(c,(int(obj.x*w),int(obj.y*h)),50,(100,170,230),-1)
            if hand.tracked:cv2.circle(c,(int(hand.x*w),int(hand.y*h)),10,(60,160,60),-1)
            if frame is not None:
                preview=cv2.resize(cv2.flip(frame,1),(240,160))
                for x,y in hand.points:cv2.circle(preview,(int(x*240),int(y*160)),2,(0,220,0),-1)
                c[450:610,690:930]=preview
            cv2.imshow(window,c);key=cv2.waitKey(16)&255
            if key==ord('q'):break
            if key==ord('m'):
                if cap:cap.release();cap=None
                if tracker:tracker.close();tracker=None
                source='mouse';f=InputFilter(1);mouse['down']=False;obj=DragObject(.3,.5);error=''
            if key==ord('h') and source!='hand':
                from utils.gesture_tracker import GestureTracker
                try:
                    tracker=GestureTracker(Path(__file__).with_name('hand_landmarker.task'))
                    cap=cv2.VideoCapture(args.camera)
                    if not cap.isOpened():raise RuntimeError('Camera access denied/unavailable')
                    source='hand';obj=DragObject(.3,.5);error=''
                except Exception as exc:
                    if cap:cap.release();cap=None
                    if tracker:tracker.close();tracker=None
                    error=str(exc);print(error,flush=True)
    finally:
        if cap:cap.release()
        if tracker:tracker.close()
        cv2.destroyAllWindows()
if __name__=='__main__':run()
