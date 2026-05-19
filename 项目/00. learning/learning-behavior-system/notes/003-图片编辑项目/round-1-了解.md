ANR_EXCEPTION
Find process anr, but unable to get anr message.
0
ANR_EXCEPTION: Find process anr, but unable to get anr message.
1
android.os.MessageQueue.next(MessageQueue.java:376)
8
com.android.internal.os.ZygoteInit.main(ZygoteInit.java:1247)

页面跟踪：
026-04-14 12:03:24.867 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} destroyed
2026-04-14 12:03:24.864 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} stopped
2026-04-14 12:03:24.864 app switch to background
2026-04-14 12:03:24.857 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} stopped
2026-04-14 12:03:24.847 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} paused
2026-04-14 12:03:23.655 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} resumed
2026-04-14 12:03:23.652 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} started
2026-04-14 12:03:23.636 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} paused
2026-04-14 12:03:01.772 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} stopped
2026-04-14 12:03:01.334 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} resumed
2026-04-14 12:03:01.331 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} started
2026-04-14 12:03:01.330 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} postCreated
2026-04-14 12:03:01.265 com.kedacom.ovopark.ui.activity.MessageListActivity{207118062} created
2026-04-14 12:03:01.247 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} paused
2026-04-14 12:03:00.864 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} destroyed
2026-04-14 12:03:00.861 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} stopped
2026-04-14 12:03:00.444 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} resumed
2026-04-14 12:03:00.442 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} started
2026-04-14 12:03:00.428 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} paused
2026-04-14 12:02:58.544 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} stopped
2026-04-14 12:02:58.101 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} resumed
2026-04-14 12:02:58.098 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} started
2026-04-14 12:02:58.097 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} postCreated
2026-04-14 12:02:58.036 com.kedacom.ovopark.ui.activity.MessageListActivity{261821757} created
2026-04-14 12:02:58.016 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} paused
2026-04-14 12:02:55.120 com.kedacom.ovopark.ui.HomeOldActivity{237286988} stopped
2026-04-14 12:02:54.703 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} resumed
2026-04-14 12:02:54.673 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} started
2026-04-14 12:02:54.672 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} postCreated
2026-04-14 12:02:54.639 com.kedacom.ovopark.ui.activity.ConversationActivity{93884931} created


日志：
--------- beginning of main
04-14 12:27:00.237 26197 13702 E eup : #++++++++++Record By Bugly++++++++++#
04-14 12:27:00.240 26197 13702 E eup : # PKG NAME: com.kedacom.ovopark
04-14 12:27:00.240 26197 13702 E eup : # APP VER: 5.41.01
04-14 12:27:00.240 26197 13702 E eup : # SDK VER: 4.4.5.6
04-14 12:27:00.240 26197 13702 E eup : # LAUNCH TIME: 2026-04-14 09:50:30
04-14 12:27:00.240 26197 13702 E eup : # CRASH TYPE: ANR
04-14 12:27:00.241 26197 13702 E eup : # CRASH TIME: 2026-04-14 12:27:00
04-14 12:27:00.242 26197 13702 E eup : # CRASH PROCESS: com.kedacom.ovopark
04-14 12:27:00.242 26197 13702 E eup : # CRASH FOREGROUND: false
04-14 12:27:00.242 26197 13702 E eup : # CRASH THREAD: main
04-14 12:27:00.244 26197 13702 E eup : # REPORT ID: 8300270d-639c-4e1e-a004-a82ef8040a4a
04-14 12:27:00.245 26197 13702 E eup : # CRASH DEVICE: BLK-AL80 UNROOT
04-14 12:27:00.246 26197 13702 E eup : # RUNTIME AVAIL RAM:4093861888 ROM:204917960704 SD:204917952512
04-14 12:27:00.246 26197 13702 E eup : # RUNTIME TOTAL RAM:12160905216 ROM:499289948160 SD:499289948160
04-14 12:27:00.247 26197 13702 E eup : # EXCEPTION ANR MESSAGE:
04-14 12:27:00.247 26197 13702 E eup : null
04-14 12:27:00.247 26197 13702 E eup : # CRASH STACK:
04-14 12:27:00.247 26197 13702 E eup : android.os.MessageQueue.next(MessageQueue.java:376)
04-14 12:27:00.247 26197 13702 E eup : android.os.Looper.loopOnce(Looper.java:163)
04-14 12:27:00.247 26197 13702 E eup : android.os.Looper.loop(Looper.java:293)
04-14 12:27:00.247 26197 13702 E eup : android.app.ActivityThread.loopProcess(ActivityThread.java:10170)
04-14 12:27:00.247 26197 13702 E eup : android.app.ActivityThread.main(ActivityThread.java:10159)
04-14 12:27:00.247 26197 13702 E eup : java.lang.reflect.Method.invoke(Native Method)
04-14 12:27:00.247 26197 13702 E eup : com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:593)
04-14 12:27:00.247 26197 13702 E eup : com.android.internal.os.ZygoteInit.main(ZygoteInit.java:1247)
04-14 12:27:00.247 26197 13702 E eup : #++++++++++++++++++++++++++++++++++++++++++#