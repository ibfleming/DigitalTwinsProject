# Digital Twins Project
*Digital twins group project for CS404.*

**Uses Git LFS!**

**Uses the FlatNodes Plugin from the Unreal Engine Marketplace!**

- [Styling Guide](https://github.com/Allar/ue5-style-guide?tab=readme-ov-file)

#### Steps to add repo to local:
1. Create empty project folder on local drive
2. Using command line type these commands in order:
3. git init
4. git lfs install
5. git remote add origin https://github.com/ibfleming/DigitalTwinsProject.git
6. git remote -v (to verify that the remote has been added)
7. git pull
- Repo should be succesfully added: Use 'git push -u origin main' to upload code to remote

[MQTT Test/Info](https://test.mosquitto.org/)

[Interactable 3D UI with unlockable mouse cursor](https://randomcreations.wtf/b/interactive-3d-ui-with-unlockable-mouse-cursor/)
- https://www.youtube.com/watch?v=_1zWWabWof0

---

#### Need to impliment:
1. Set the mode: Either be on "replay mode" so show historical data, or be on "real time mode" which is what we already have implimented.
2. Need to tie the replay to the timestamps that we are taking when storing the real time data into the arrow data base.
3. Basically need to set a delay of some sort to get the replay in real time.
4. Replay manager will have to have a clock implimentation. (Unreal already provides us with a really good clock that we can use to impliment this)
