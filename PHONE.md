# ביצוע מהטלפון בלבד (בלי מחשב) – YouTube + yes+

## מה לא נוגעים בו בשום מסלול (שליטה מרחוק)
אסור לכבות: **Bluetooth**, **Android TV Remote Service** (שליטה מאפליקציית טלפון), **Google / חיפוש קולי** (מיקרופון בשלט), **Chromecast built-in**, **מקלדת**, **הגדרות**, **מסך הבית (Android TV Home)**, **Google Play Services / Play Store**, וכל אפליקציה שמתחילה ב-**TCL** (כולל HDMI-CEC – שליטה בשלט אחד על מקלט/מגבר).

שים לב: אם מכבים Netflix, הכפתור Netflix בשלט פשוט לא יעשה כלום. זה לא פוגע בשאר השלט.

## מסלול א' – עם השלט בלבד (עובד עם אייפון ואנדרואיד, מומלץ להתחיל כאן)
1. הגדרות ← אפליקציות ← "ראה את כל האפליקציות" (ו"הצג אפליקציות מערכת" אם יש).
2. לכל אפליקציה **שאינה** YouTube / yes+ / ברשימת "לא נוגעים": לחץ עליה ←
   - "הסר התקנה" אם קיים, אחרת
   - "השבת" (Disable). אם מופיעה אזהרה ש"אפליקציות אחרות עלולות לא לפעול" – **בטל ודלג** עליה.
3. מועמדים טיפוסיים לכיבוי: Netflix, Prime Video, Disney+, Spotify, YouTube Music, YouTube Kids, Google Play Movies/TV, Google Play Games, Google Play Music, Facebook, Plex, Twitch, משחקים.
4. YouTube ו-yes+: "נקה מטמון" (לא "נקה נתונים").
5. מסך הבית: לחיצה ארוכה ← "הסר ממועדפים" לכל השאר. "התאמה אישית של ערוצים" ← כבה שורות המלצות.
6. מהירות אנימציה: אפשרויות למפתחים ← Window / Transition / Animator scale ← **0.5x**.
7. ניתוק מהחשמל ל-30 שניות.

ביטול: הגדרות ← אפליקציות ← "אפליקציות מושבתות" ← הפעל.

## מסלול ב' – טלפון אנדרואיד עם אפליקציית ADB (מכבה גם מה שהתפריט לא נותן)
לא קיים כלי ADB אמין לאייפון; באייפון השתמש במסלול א'.

1. בטלוויזיה: אפשרויות למפתחים ← **USB debugging = מופעל** (ואם קיים, גם Network/ADB debugging).
2. בטלפון: התקן מ-Google Play אפליקציה שמתחברת ל-ADB ברשת, למשל **Bugjaeger** או **Remote ADB Shell**. הטלפון צריך להיות על אותו Wi-Fi.
3. התחבר ל-`<IP של הטלוויזיה>:5555` ואשר את הבקשה שעל המסך בטלוויזיה ("Always allow").
4. בדיקה – הדבק והרץ, ושלח את הפלט לבדיקה לפני שממשיכים:
   ```
   pm list packages -3
   ```
5. כיבוי (הפקודות בטוחות להעתקה כמו שהן; חבילה שלא קיימת פשוט תחזיר שגיאה):
   ```
   pm disable-user --user 0 com.netflix.ninja
   pm disable-user --user 0 com.amazon.amazonvideo.livingroom
   pm disable-user --user 0 com.disney.disneyplus
   pm disable-user --user 0 com.spotify.tv.android
   pm disable-user --user 0 com.google.android.youtube.tvmusic
   pm disable-user --user 0 com.google.android.youtube.tvkids
   pm disable-user --user 0 com.google.android.videos
   pm disable-user --user 0 com.google.android.music
   pm disable-user --user 0 com.google.android.play.games
   pm disable-user --user 0 com.google.android.tvrecommendations
   pm disable-user --user 0 com.google.android.feedback
   settings put global window_animation_scale 0.5
   settings put global transition_animation_scale 0.5
   settings put global animator_duration_scale 0.5
   reboot
   ```
   אפליקציות נוספות מהפלט של שלב 4 – רק אחרי בדיקה.
6. ביטול: אותה פקודה עם `pm enable <שם החבילה>`, ו-`settings put global ... 1.0`.

שם החבילה של yes+ לפי APKMirror: `il.co.yes.yesplus` – לא לגעת בו.
