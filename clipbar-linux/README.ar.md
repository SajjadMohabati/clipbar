<div dir="rtl">

<p align="center">
  <img src="resources/clipbar.svg" width="150" alt="ClipBar مدير الحافظة المجاني لنظام لينكس">
</p>

<h1 align="center">ClipBar لنظام لينكس | مدير الحافظة المجاني الذي لا يُضيع ما تكتبه</h1>

<p align="center">
  <b>سجل حافظة مجاني ومفتوح المصدر لأوبونتو وديبيان وفيدورا وآرتش، بثيم داكن نظيف وأصلي</b><br>
  <b>Drafts: استرجاع النص الذي كتبته وفقدته</b> · عناصر مقفلة ومشفّرة · لقطات الشاشة في السجل · البحث في النص داخل الصور · لصق فوري
</p>

<p align="center">
  <a href="https://github.com/SajjadMohabati/clipbar/releases/tag/linux-v1.0.1"><img src="https://img.shields.io/badge/download-1.0.1-7c5cff" alt="تنزيل ClipBar لنظام لينكس 1.0.1"></a>
  <img src="https://img.shields.io/badge/Ubuntu-24.04%2B-E95420?logo=ubuntu&logoColor=white" alt="أوبونتو 24.04 وأحدث">
  <img src="https://img.shields.io/badge/Debian-12%2B-A81D33?logo=debian&logoColor=white" alt="ديبيان 12 وأحدث">
  <img src="https://img.shields.io/badge/X11%20%2B%20Wayland-supported-555" alt="X11 وWayland">
  <img src="https://img.shields.io/badge/Qt-6-41CD52?logo=qt&logoColor=white" alt="Qt 6">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="رخصة MIT"></a>
</p>

<p align="center">
  <a href="#install"><b>⬇️ التثبيت</b></a>
  &nbsp;·&nbsp; <a href="#drafts">المسودات</a>
  &nbsp;·&nbsp; <a href="#features">المزايا</a>
  &nbsp;·&nbsp; <a href="#wayland">Wayland</a>
  &nbsp;·&nbsp; <a href="#shortcuts">الاختصارات</a>
  &nbsp;·&nbsp; <a href="#faq">الأسئلة الشائعة</a>
</p>

<p align="center">
  <img src="../docs/linux-panel.png" width="400" alt="لوحة سجل الحافظة في ClipBar على لينكس مع البحث والفلاتر والعناصر المثبّتة">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <a href="README.fa.md">فارسی</a> &nbsp;·&nbsp; <a href="../README.ar.md">🍎 ClipBar لماك</a></p>

<p align="center"><sub>من تطوير <a href="https://github.com/SajjadMohabati"><b>سجاد محبتي (Sajjad Mohabati)</b></a></sub></p>

---

يحتفظ ClipBar بكل ما تنسخه على لينكس: النصوص والروابط والألوان والصور والملفات. اضغط `Ctrl+Shift+V`، واختر العنصر، فيُلصق حيث كنت تكتب. ويحتفظ أيضًا بنسخة من **ما تكتبه** في التطبيقات الأخرى، فلا تخسر نصك إذا أُعيد تحميل نموذج أو فشل إرسال رسالة.

<a id="drafts"></a>

## Drafts: استرجاع النص الذي كتبته وفقدته

تكتب رسالة طويلة، وتضغط إرسال، فتختفي. أُعيد تحميل الصفحة، أو انتهت الجلسة، أو أُغلق التطبيق، أو أغلقت التبويب بالخطأ.

**ميزة Drafts في ClipBar تحفظ ما تكتبه أثناء كتابته**، في أي تطبيق يدعم إمكانية الوصول في لينكس، حتى لو لم تنسخه. افتح ClipBar، وانتقل إلى تبويب **Drafts**، والصقه من جديد.

| ماذا حدث | ماذا يفعل ClipBar |
| --- | --- |
| أُعيد ضبط نموذج الموقع أو أُعيد تحميل الصفحة | نصك موجود في Drafts |
| «فشل إرسال الرسالة» وأصبح الحقل فارغًا | نصك موجود في Drafts |
| أغلقت التبويب أو أُغلق التطبيق | نصك موجود في Drafts |
| حدّدت النص كله وكتبت فوقه بالخطأ | النسخة السابقة موجودة في Drafts |

**كيف تعمل**

1. فعّلها مرة واحدة من **Settings → Drafts**.
2. اكتب في أي مكان: المتصفح، وتطبيقات المراسلة، والبريد، والنماذج، والملاحظات.
3. يحتفظ ClipBar **بمسودة واحدة لكل رسالة**. تتحدّث أثناء الكتابة، وعندما يُفرَّغ الحقل (أُرسل أو مُسح) يبقى النص كاملًا في Drafts.
4. فقدت شيئًا؟ اضغط `Ctrl+Shift+V`، وافتح **Drafts**، ثم اضغط `Enter`.

**آمنة وخاصة**

- **ليست مسجّل مفاتيح.** لا يستمع ClipBar إلى لوحة المفاتيح أبدًا، بل يسأل خدمة إمكانية الوصول في لينكس (AT-SPI) مرة كل ثانية عن نص الحقل النشط.
- **لا يقرأ أبدًا** حقول كلمات المرور أو البحث، ويتجاهل الطرفيات ومديري كلمات المرور وأي تطبيق لا يستطيع التعرف عليه، على X11 وWayland على حد سواء.
- لا تُحفظ أرقام البطاقات ومفاتيح API، وتنتهي صلاحية المسودات تلقائيًا، ولا يغادر شيء جهازك.
- **معطّلة افتراضيًا.** أنت تحدد الحد الأدنى للطول (30 حرفًا)، ومدة الاحتفاظ (12 ساعة)، والعدد (10).
- تدعم العربية والنصوص من اليمين إلى اليسار بالكامل.

<a id="features"></a>

## المزايا

### سجل الحافظة
- يحفظ **النصوص والروابط والألوان والصور والملفات** مع وقت نسخها.
- **الفلاتر:** الكل · المثبّت · النص · الروابط · الصور · الملفات (`Tab` و`Shift+Tab`).
- **بحث فوري** في النصوص والعناوين والنص المستخرج من الصور.
- **تثبيت** العناصر المهمة في الأعلى. نسخ الشيء نفسه مرة أخرى يرفعه إلى الأعلى بدل تكراره.
- **تنظيف تلقائي** حسب العمر (من 1 إلى 365 يومًا) والعدد (من 50 إلى 2000 عنصر)، ويمكن إبقاء العناصر المثبّتة دائمًا.

### العناصر المحفوظة والقفل المشفّر
- قائمة **Saved** منفصلة لما تلصقه مرارًا: رقم البطاقة، والعنوان، وتوقيع البريد.
- **أعطِ أي عنصر محفوظ عنوانًا**، نصًا كان أو صورة، والعناوين قابلة للبحث.
- **اقفل العنصر** فتُشفَّر قيمته بخوارزمية **AES-256-GCM** بمفتاح مشتق من كلمة مرور ClipBar عبر **scrypt**. لا تُحفظ كلمة المرور أبدًا، فلا تستطيع كلمة مرور خاطئة أو فارغة فك التشفير.
- بعد فتح القفل لديك 30 ثانية، ثم يُمحى المفتاح من الذاكرة.

### لقطات الشاشة والتعرف على النص
- تُضاف لقطات الشاشة الجديدة في `~/Pictures/Screenshots` (أو مجلد Pictures) **إلى السجل وتُنسخ إلى الحافظة تلقائيًا**.
- **التعرف على النص داخل الصور** عبر Tesseract على جهازك، فيصبح نص الصور قابلًا للبحث.

### اللصق والتحرير
- **لصق مباشر:** `Enter` يلصق في التطبيق الذي كنت فيه، و`Alt+Enter` ينسخ فقط.
- **`Ctrl+1` إلى `Ctrl+9`** تلصق العناصر التسعة الأولى فورًا.
- **محرر كامل** مع عدد الأحرف والكلمات والأسطر، وقيم الألوان (HEX وRGB وHSL)، ونص الصور.
- **تحويلات بنقرة واحدة:** أحرف كبيرة وصغيرة، Capitalize، حذف المسافات والأسطر الفارغة، الترتيب، حذف المكرر، دمج الأسطر، تنسيق JSON أو ضغطه، ترميز Base64 وURL وفكّه.

### الخصوصية
- يتجاهل **المفاتيح الخاصة ورموز API** (GitHub وOpenAI وStripe وAWS وSlack وGoogle…) و**أرقام البطاقات المصرفية** (بفحص Luhn).
- **إيقاف الالتقاط مؤقتًا** من قائمة أيقونة شريط النظام.
- بلا حساب، وبلا سحابة، وبلا إحصاءات، وبلا أي طلب عبر الإنترنت.

<a id="install"></a>

## التثبيت

### أوبونتو وديبيان (موصى به)

نزّل الملف **`clipbar_1.0.1_all.deb`** من [صفحة أحدث إصدار للينكس](https://github.com/SajjadMohabati/clipbar/releases/tag/linux-v1.0.1) وثبّته:

<div dir="ltr">

```bash
sudo apt install ./clipbar_1.0.1_all.deb
```

</div>

ولميزة Drafts ثبّت أيضًا حزم إمكانية الوصول:

<div dir="ltr">

```bash
sudo apt install python3-gi gir1.2-atspi-2.0 at-spi2-core
```

</div>

ثم افتح **ClipBar** من قائمة التطبيقات (أو شغّل `clipbar`) واضغط `Ctrl+Shift+V`. لتشغيله مع بدء سطح المكتب، فعّل **Launch at login** من Settings → General.

### فيدورا

<div dir="ltr">

```bash
sudo dnf install python3-pyqt6 python3-cryptography python3-gobject at-spi2-core xdotool tesseract
git clone https://github.com/SajjadMohabati/clipbar.git
cd clipbar/clipbar-linux && ./build.sh install
```

</div>

### آرتش لينكس ومانجارو

<div dir="ltr">

```bash
sudo pacman -S python-pyqt6 python-cryptography python-gobject at-spi2-core xdotool tesseract tesseract-data-eng
git clone https://github.com/SajjadMohabati/clipbar.git
cd clipbar/clipbar-linux && ./build.sh install
```

</div>

يثبّت الأمر `./build.sh install` برنامج ClipBar في `~/.local` مع اختصار في القائمة، مستخدمًا حزم Python الخاصة بالنظام، ويزيله الأمر `./build.sh uninstall`. لتجربته دون تثبيت، شغّل `python3 -m clipbar.main` من مجلد `clipbar-linux`.

| الحزمة | الغرض |
| --- | --- |
| `python3-pyqt6`، `python3-pyqt6.qtsvg` | التطبيق نفسه (مطلوبة) |
| `python3-cryptography` | العناصر المقفلة (مطلوبة) |
| `python3-gi`، `gir1.2-atspi-2.0`، `at-spi2-core` | Drafts |
| `xdotool` (X11)، `wtype` أو `ydotool` (Wayland) | اللصق المباشر |
| `tesseract-ocr` | النص داخل الصور |
| `python3-pynput` | الاختصار العام على X11 |

### التجربة عبر Docker

على أي جهاز فيه Docker، حتى ماك، يمكنك معاينة نسخة لينكس في المتصفح:

<div dir="ltr">

```bash
cd clipbar-linux && ./run-docker.sh
```

</div>

ثم افتح <http://localhost:6080/vnc.html?autoconnect=true&resize=scale>.

<a id="wayland"></a>

## Wayland

يعمل ClipBar على جلسات Wayland في GNOME وKDE:

- **سجل الحافظة:** في Wayland لا يقرأ الحافظة إلا النافذة النشطة، لذلك يتابع ClipBar الحافظة تلقائيًا عبر XWayland حيث تكون مشتركة بين جميع التطبيقات.
- **الاختصار:** لا يسمح Wayland للتطبيقات بحجز مفاتيح عامة. أضف اختصارًا من إعدادات لوحة المفاتيح في سطح المكتب (GNOME: *Settings → Keyboard → Custom Shortcuts*، KDE: *System Settings → Shortcuts*) بالأمر `clipbar --toggle` والمفاتيح `Ctrl+Shift+V`.
- **اللصق المباشر:** ثبّت `wtype` (لـ Sway وHyprland) أو `ydotool` (لـ GNOME وKDE). بدونهما ينسخ ClipBar العنصر وتضغط أنت `Ctrl+V`.
- **Drafts:** تعمل كما في X11 تمامًا، عبر AT-SPI.

<a id="shortcuts"></a>

## اختصارات لوحة المفاتيح

| المفتاح | الوظيفة |
| --- | --- |
| `Ctrl+Shift+V` | فتح ClipBar (يمكن تغييره من الإعدادات) |
| `↑` `↓` | التنقل بين العناصر |
| `Enter` | لصق العنصر المحدد |
| `Alt+Enter` | نسخ دون لصق |
| `Ctrl+1` إلى `Ctrl+9` | لصق العنصر من 1 إلى 9 |
| `Tab` / `Shift+Tab` | الفلتر التالي / السابق |
| `Ctrl+[` / `Ctrl+]` | التبويب السابق / التالي (السجل، المسودات، المحفوظة) |
| `Ctrl+S` | النقل إلى المحفوظة |
| `Ctrl+P` | تثبيت أو إلغاء التثبيت |
| `Ctrl+E` | العرض والتحرير |
| `Ctrl+Backspace` | الحذف |
| `Ctrl+,` | الإعدادات |
| `Esc` | مسح البحث، ثم إغلاق اللوحة |

من الطرفية: `clipbar --toggle` يفتح اللوحة أو يغلقها، و`clipbar --settings` يفتح الإعدادات.

<a id="faq"></a>

## الأسئلة الشائعة

<details>
<summary><b>ما أفضل مدير حافظة لأوبونتو؟</b></summary>

ClipBar مدير حافظة مجاني ومفتوح المصدر لأوبونتو، فيه السجل والبحث والعناصر المثبّتة والمحفوظة والقفل المشفّر ولقطات الشاشة والتعرف على النص، إضافة إلى Drafts التي تسترجع النص المكتوب المفقود. ثبّت حزمة `.deb` من [صفحة الإصدار](https://github.com/SajjadMohabati/clipbar/releases/tag/linux-v1.0.1).
</details>

<details>
<summary><b>كيف أعرض سجل الحافظة في لينكس؟</b></summary>

ثبّت ClipBar واضغط `Ctrl+Shift+V`. يظهر كل ما نسخته منذ تشغيل ClipBar من الأحدث إلى الأقدم، ويمكنك البحث فيه وتصفيته ولصق أي عنصر بالضغط على `Enter`.
</details>

<details>
<summary><b>كيف أسترجع نصًا كتبته في لينكس ثم اختفى؟</b></summary>

فعّل ميزة **Drafts** من الإعدادات. من بعدها يحتفظ ClipBar بنسخة من النصوص الطويلة أثناء كتابتها. إذا أُعيد ضبط النموذج أو فشل إرسال الرسالة، افتح تبويب **Drafts** والصق النص من جديد. لا يمكن استرجاع ما كُتب قبل تفعيل Drafts.
</details>

<details>
<summary><b>هل ميزة Drafts مسجّل مفاتيح؟</b></summary>

لا. لا يقرأ ClipBar لوحة المفاتيح أبدًا، بل يسأل خدمة إمكانية الوصول مرة كل ثانية عن نص الحقل النشط، ولا يقرأ حقول كلمات المرور أو البحث، ويتجاهل الطرفيات ومديري كلمات المرور والتطبيقات غير المعروفة. وهي معطّلة حتى تفعّلها، وتبقى بياناتها على جهازك.
</details>

<details>
<summary><b>ما مدى أمان العناصر المقفلة؟</b></summary>

تُشفَّر بخوارزمية AES-256-GCM. يُشتق المفتاح من كلمة مرور ClipBar عبر scrypt ولا يُكتب على القرص أبدًا، فلا يمكن فتح الملف المشفّر دون كلمة المرور. إذا نسيت كلمة المرور فلا يمكن استرجاع العناصر المقفلة.
</details>

<details>
<summary><b>هل يعمل ClipBar على Wayland؟</b></summary>

نعم، على GNOME وKDE. راجع قسم [Wayland](#wayland) لإعداد الاختصار العام واللصق المباشر.
</details>

<details>
<summary><b>هل ClipBar لنظام لينكس مجاني؟</b></summary>

نعم. مجاني ومفتوح المصدر برخصة MIT، بلا حساب ولا اشتراك ولا تتبّع.
</details>

## بياناتك

يستخدم ClipBar مجلدات XDG القياسية:

- `~/.local/share/clipbar/history.json`: سجل الحافظة
- `~/.local/share/clipbar/saved.json`: العناصر المحفوظة (قيم العناصر المقفلة مشفّرة في `vault.enc` فقط)
- `~/.local/share/clipbar/drafts.json`: المسودات، إن كانت Drafts مفعّلة
- `~/.local/share/clipbar/images/`: الصور المنسوخة، تُحفظ كل صورة مرة واحدة بصيغة PNG
- `~/.config/clipbar/settings.json`: الإعدادات

للبدء من جديد، أغلق ClipBar واحذف هذه المجلدات.

## المطوّر

من تطوير **سجاد محبتي (Sajjad Mohabati)** · [github.com/SajjadMohabati](https://github.com/SajjadMohabati)

إن أفادك ClipBar، فنجمة ⭐️ على [GitHub](https://github.com/SajjadMohabati/clipbar) تساعد الآخرين على العثور عليه.

## الرخصة

[MIT](LICENSE) © سجاد محبتي (Sajjad Mohabati)

<sub>كلمات مفتاحية: مدير الحافظة لينكس، سجل الحافظة لينكس، مدير الحافظة أوبونتو، برنامج الحافظة ديبيان، حافظة فيدورا، حافظة آرتش لينكس، حافظة Wayland، سجل الحافظة GNOME، حافظة KDE، استرجاع النص المكتوب في لينكس، استعادة رسالة لم تُرسل، حفظ تلقائي للنص المكتوب، إدارة النسخ واللصق في لينكس، حافظة مشفّرة، لقطة الشاشة إلى الحافظة، التعرف على النص في الصور لينكس، مدير حافظة مجاني ومفتوح المصدر، clipboard manager for Linux.</sub>

</div>
