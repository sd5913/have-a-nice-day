"""Standalone Little Cat Chef. Run: python -m games.little_chef.demo."""
import argparse
from pathlib import Path
from time import monotonic
import cv2
from games.little_chef.game import ChefGame
from games.little_chef.view import draw_chef
from .visuals import Visuals
from utils.hand_input import InputFilter

W,H=960,640

def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--camera',type=int,default=0)
    parser.add_argument('--hand',action='store_true',help='Start in webcam mode')
    args=parser.parse_args()
    start_hand=args.hand
    visuals=Visuals(Path(__file__).with_name('assets'))
    window='Little Cat Chef'
    cv2.namedWindow(window)
    mouse={'x':.3,'y':.5,'down':False,'inside':True,'ui_click':False}
    def event(kind,x,y,flags,param):
        mouse.update(x=x/W,y=y/H,inside=0<=x<W and 0<=y<H)
        if kind==cv2.EVENT_LBUTTONDOWN:
            mouse['down']=True
            if 336<=x<=653 and 563<=y<=620: mouse['ui_click']=True
        if kind==cv2.EVENT_LBUTTONUP: mouse['down']=False
    cv2.setMouseCallback(window,event)
    source='mouse'; tracker=cap=None; message='Mouse mode ready'; camera_error='' 
    filt=InputFilter(smoothing=1)
    chef=ChefGame(); last=monotonic()
    try:
        while True:
            if source=='hand':
                ok,frame=cap.read()
                if ok: hand=tracker.update(cv2.flip(frame,1))
                else:
                    hand=tracker.processor.filter.update(tracked=False)
                    message='Camera unavailable. Press M for mouse.'
            else:
                hand=filt.update(mouse['x'],mouse['y'],mouse['down'],tracked=mouse['inside'],source='mouse')
            now=monotonic(); dt=now-last; last=now
            if mouse['ui_click'] and source=='hand': chef.activate_button()
            chef.update(hand,dt)
            mouse['ui_click']=False
            status=('Open hand / release once' if not hand.ready else ('Holding' if hand.pinched else 'Ready')) if hand.tracked else 'Tracking lost - paused; show hand or press M'
            if chef.stage in ('approach','eat','result') and not hand.tracked:
                status='Cat is playing its reaction - hands can rest'
            canvas=draw_chef(visuals,chef,source.upper()+' | '+status)
            if source=='hand' and ok:
                preview=cv2.resize(cv2.flip(frame,1),(180,120))
                for px,py in hand.points:
                    cv2.circle(preview,(int(px*180),int(py*120)),2,(0,220,80),-1)
                canvas[10:130,770:950]=preview
            if camera_error:
                import textwrap
                cv2.rectangle(canvas,(12,165),(948,255),(225,230,255),-1)
                for i,line in enumerate(textwrap.wrap(camera_error,105)[:4]):
                    cv2.putText(canvas,line,(24,188+i*19),cv2.FONT_HERSHEY_SIMPLEX,.47,(30,30,155),1,cv2.LINE_AA)
            if hand.tracked:
                cv2.circle(canvas,(int(hand.x*W),int(hand.y*H)),10,(80,150,50) if hand.pinched else (150,90,80),-1)
            cv2.imshow(window,canvas)
            key=cv2.waitKey(16)&255
            if start_hand: key=ord('h'); start_hand=False
            if key in (ord('q'),27) or cv2.getWindowProperty(window,cv2.WND_PROP_VISIBLE)<1: break
            if key in (8,127): chef.remove_last()
            if key in (13,10): chef.activate_button()
            if key==ord('r'):
                chef=ChefGame(chef.round_index,chef.affection)
                filt.update(tracked=False)
                if tracker: tracker.processor.filter.update(tracked=False)
            if key in (ord('m'),ord('h')) and chef.held:
                item=chef.items[chef.held]; item.x,item.y=item.start; item.held=False; chef.held=None
                chef.stir.last=None
            if key==ord('m'):
                camera_error=''
                source='mouse'; filt=InputFilter(smoothing=1); mouse['down']=False
                message='Mouse: move, hold left button, release.'
                if cap: cap.release(); cap=None
                if tracker: tracker.close(); tracker=None
            if key==ord('h') and source!='hand':
                from utils.gesture_tracker import GestureTracker
                try:
                    tracker=GestureTracker(Path(__file__).resolve().parents[2]/'hand_landmarker.task')
                    cap=cv2.VideoCapture(args.camera)
                    if not cap.isOpened(): raise RuntimeError('Camera access denied/unavailable')
                    source='hand'; camera_error=''; message='Show an open hand, then pinch.'
                except Exception as exc:
                    if cap: cap.release(); cap=None
                    if tracker: tracker.close(); tracker=None
                    camera_error='CAMERA START FAILED: '+str(exc)
                    message='Mouse mode. See camera error above.'
                    # Report setup errors without writing machine-specific logs into the source tree.
                    print(camera_error,flush=True)
    finally:
        if cap: cap.release()
        if tracker: tracker.close()
        cv2.destroyAllWindows()

if __name__=='__main__': run()
