/* Beside translations. Keys are the English text; add a new language by adding another table.
   Stored data (log, diary) is always kept in English and translated only for display. */
(function (root) {
  "use strict";

  const TR = {
    // consent
    "Before we start": "Başlamadan önce",
    "Beside watches over you at night and asks the people you choose to check on you. To do that it needs a few permissions. You can change your mind at any time in your phone settings.":
      "Beside gece seni gözetir ve seçtiğin kişilerden seni kontrol etmelerini ister. Bunun için birkaç izne ihtiyacı var. Bu izinleri istediğin zaman telefonunun ayarlarından değiştirebilirsin.",
    "Movement sensor": "Hareket sensörü",
    "To notice the strong, rhythmic movements of a convulsive seizure while you sleep.": "Uyurken kasılmalı bir nöbetin güçlü ve ritmik hareketlerini fark etmek için.",
    "Location": "Konum",
    "Only added to an emergency message, so your contacts know where to come.": "Sadece acil durum mesajına eklenir; yakınların nereye geleceğini bilsin diye.",
    "Microphone": "Mikrofon",
    "Only while aura listening is on, to hear your code word. Audio is not recorded or sent.": "Sadece aura dinleme açıkken, kod kelimeni duymak için. Ses kaydedilmez ve gönderilmez.",
    "Your health log": "Sağlık günlüğün",
    "Saved only on this phone. It leaves the phone only when you choose to share a report.": "Sadece bu telefonda saklanır. Telefondan yalnızca sen bir rapor paylaşmayı seçersen çıkar.",
    "Beside is a research prototype, not a medical device.": "Beside bir araştırma prototipidir, tıbbi cihaz değildir.",
    "It can miss seizures and it can raise false alarms. Keep following your doctor's safety advice.": "Nöbetleri kaçırabilir ve yanlış alarm verebilir. Doktorunun güvenlik önerilerine uymaya devam et.",
    "I understand, allow": "Anladım, izin ver",

    // settings
    "Done": "Bitti",
    "Your safety plan": "Güvenlik planın",
    "Stored only on this phone. Nothing is sent to a server.": "Sadece bu telefonda saklanır. Hiçbir şey bir sunucuya gönderilmez.",
    "Language": "Dil",
    "From your doctor": "Doktorundan",
    "Seizure type": "Nöbet türü",
    "Tonic-clonic (including focal to bilateral)": "Tonik-klonik (fokalden iki taraflıya dönüşen dahil)",
    "Focal with movement": "Hareketli fokal",
    "Focal without movement": "Hareketsiz fokal",
    "Typical seizure length (seconds)": "Tipik nöbet süresi (saniye)",
    "If a seizure lasts longer than this, your contacts are told it is longer than usual.": "Bir nöbet bundan uzun sürerse, yakınlarına her zamankinden uzun sürdüğü söylenir.",
    "Your doctor": "Doktorun",
    "Name": "Ad",
    "Email for reports": "Raporlar için e-posta",
    "Your doctor gets a report only when you share it. Emergency messages go to the people below, not to your doctor, because a doctor may not see a message at night.":
      "Doktoruna rapor sadece sen paylaştığında gider. Acil durum mesajları doktoruna değil aşağıdaki kişilere gider, çünkü doktor gece mesajı göremeyebilir.",
    "Aura": "Aura",
    "Your code word": "Kod kelimen",
    "Say it when you feel an aura. It turns on high-attention mode; it never calls an ambulance by itself.": "Aura hissettiğinde bunu söyle. Yüksek dikkat modunu açar; kendi başına asla ambulans çağırmaz.",
    "People to contact": "Haber verilecek kişiler",
    "Add a person": "Kişi ekle",
    "Phone": "Telefon",
    "Remove": "Kaldır",
    "Send my messages by": "Mesajlarımı şununla gönder",
    "Beside writes the message and opens it for you; you tap Send. A website is not allowed to send messages on its own.":
      "Beside mesajı yazar ve senin için açar; sen Gönder'e basarsın. Bir web sitesinin kendi başına mesaj göndermesine izin verilmez.",
    "Automatic alert (optional)": "Otomatik uyarı (isteğe bağlı)",
    "Send alerts automatically with ntfy": "Uyarıları ntfy ile otomatik gönder",
    "On your contact's phone:": "Yakınının telefonunda:",
    "Install the free": "Ücretsiz",
    "app (App Store or Google Play).": "uygulamasını kur (App Store ya da Google Play).",
    "Tap": "",
    "(Subscribe to topic) and type this family code:": "simgesine (Subscribe to topic) dokun ve şu aile kodunu yaz:",
    "Send a test alert": "Deneme uyarısı gönder",
    "When this is on, Beside sends the alert by itself if nobody answers the check-in, and when you report an aura. Only the alert text and your location go through the ntfy.sh service; anyone who knows the code can read these alerts, so share it only with your contacts. SMS and WhatsApp buttons stay available as a backup.":
      "Bu açıkken, kontrole kimse cevap vermezse ya da aura bildirirsen Beside uyarıyı kendisi gönderir. Sadece uyarı metni ve konumun ntfy.sh servisinden geçer; kodu bilen herkes bu uyarıları okuyabilir, bu yüzden kodu yalnızca yakınlarınla paylaş. SMS ve WhatsApp butonları yedek olarak kalır.",
    "Comfort and light": "Rahatlık ve ışık",
    "Beside never flashes or flickers. To soften flashing in other apps too, your iPhone has a built-in setting:": "Beside asla yanıp sönmez ve titremez. Diğer uygulamalardaki yanıp sönmeleri de yumuşatmak için iPhone'unda hazır bir ayar var:",
    "Settings → Accessibility → Motion → Dim Flashing Lights": "Ayarlar → Erişilebilirlik → Hareket → Yanıp Sönen Işıkları Karart",
    "Ask your doctor whether light sensitivity matters for your type of epilepsy.": "Işık hassasiyetinin senin epilepsi türün için önemli olup olmadığını doktoruna sor.",
    "Save": "Kaydet",
    "Research prototype. Not a medical device.": "Araştırma prototipi. Tıbbi cihaz değildir.",

    // home
    "Settings": "Ayarlar",
    "Good morning": "Günaydın",
    "Good afternoon": "İyi günler",
    "Good evening": "İyi akşamlar",
    "Not watching right now": "Şu an izlemiyor",
    "Watching over you": "Seni izliyor",
    "Start sleep mode before you go to bed.": "Yatmadan önce uyku modunu başlat.",
    "Add a contact in Settings.": "Ayarlar'dan bir kişi ekle.",
    "Time for your monthly report": "Aylık rapor zamanı",
    "Share the last 30 days with your doctor.": "Son 30 günü doktorunla paylaş.",
    "Open report": "Raporu aç",
    "Start sleep mode": "Uyku modunu başlat",
    "I feel an aura": "Aura hissediyorum",
    "Message my contact now": "Yakınıma hemen mesaj",
    "My diary": "Günlüğüm",
    "Private notes, mood, sleep": "Özel notlar, ruh hali, uyku",
    "Seizure log": "Nöbet kaydı",
    "Every check-in and alert": "Tüm kontroller ve uyarılar",
    "Report for my doctor": "Doktorum için rapor",
    "Summary and spreadsheet": "Özet ve tablo",
    "Real recording": "Gerçek kayıt",
    "See how detection works": "Tespit nasıl çalışıyor",
    "Practise the check-in": "Kontrolü dene",
    "See what happens, nothing is sent": "Ne olduğunu gör, hiçbir şey gönderilmez",

    // sleep
    "Watching quietly. Sleep well.": "Sessizce izliyor. İyi uykular.",
    "Movement": "Hareket",
    "Keep the phone on the charger. The screen stays on but dark, because the phone stops web apps when it locks.": "Telefonu şarjda tut. Ekran açık ama karanlık kalır, çünkü telefon kilitlenince web uygulamalarını durdurur.",
    "This browser cannot keep the screen on. Set Auto-Lock to Never while you sleep, and keep the phone on the charger.": "Bu tarayıcı ekranı açık tutamıyor. Uyurken Otomatik Kilit'i \"Hiçbir Zaman\" yap ve telefonu şarjda tut.",
    "Seizure detection is on. It learns your normal movement during the first minutes.": "Nöbet tespiti açık. İlk dakikalarda senin normal hareketini öğrenir.",
    "Detection model not loaded; only the demo button works.": "Tespit modeli yüklenemedi; sadece demo butonu çalışır.",
    "Demo: simulate a seizure": "Demo: nöbet taklidi",
    "I'm awake, stop": "Uyandım, durdur",

    // aura
    "High-attention mode is on": "Yüksek dikkat modu açık",
    "For the next 10 minutes, Beside reacts faster to movement.": "Önümüzdeki 10 dakika boyunca Beside harekete daha hızlı tepki verir.",
    "We opened this message for you. Tap Send in your messaging app.": "Bu mesajı senin için açtık. Mesaj uygulamanda Gönder'e bas.",
    "Your contacts were notified automatically. You can also send this message yourself:": "Yakınlarına otomatik olarak haber verildi. Bu mesajı kendin de gönderebilirsin:",
    "I feel fine now": "Şimdi iyiyim",
    "I just felt an aura. Beside is watching closely for the next 10 minutes. If you get another message, please check on me.":
      "Az önce aura hissettim. Beside önümüzdeki 10 dakika beni yakından izliyor. Bir mesaj daha gelirse lütfen beni kontrol et.",

    // countdown + alert
    "Are you OK?": "İyi misin?",
    "If you do not answer, your contacts will be asked to check on you.": "Cevap vermezsen yakınlarından seni kontrol etmeleri istenecek.",
    "I'm OK": "İyiyim",
    "Asking for help": "Yardım isteniyor",
    "No answer to the check-in. Send this to your contacts:": "Kontrole cevap verilmedi. Bunu yakınlarına gönder:",
    "Your contacts were alerted automatically.": "Yakınlarına otomatik olarak haber verildi.",
    "Automatic alert failed. Please use the buttons below.": "Otomatik uyarı gönderilemedi. Lütfen aşağıdaki butonları kullan.",
    "It was a false alarm": "Yanlış alarmdı",
    "Beside alert: possible seizure. No answer to the check-in at": "Beside uyarısı: olası nöbet. Şu saatteki kontrole cevap yok:",
    "Location:": "Konum:",
    "unknown": "bilinmiyor",
    "Please call or check on me.": "Lütfen beni ara ya da yanıma gel.",
    "Sending...": "Gönderiliyor...",
    "Sent. Check your contact's phone.": "Gönderildi. Yakınının telefonuna bak.",
    "Could not send. Check the internet connection.": "Gönderilemedi. İnternet bağlantısını kontrol et.",

    // log
    "Back": "Geri",
    "Every check-in is saved here so you can show your doctor.": "Her kontrol burada kaydedilir, böylece doktoruna gösterebilirsin.",
    "Nothing yet.": "Henüz bir şey yok.",
    "Aura reported": "Aura bildirildi",
    "Sleep mode": "Uyku modu",
    "Practice check-in": "Deneme kontrolü",
    "Check-in (demo)": "Kontrol (demo)",
    "Possible seizure detected": "Olası nöbet tespit edildi",
    "no answer yet": "henüz cevap yok",
    "answered: I'm OK": "cevap: iyiyim",
    "contacts alerted": "yakınlara haber verildi",
    "false alarm (after alert)": "yanlış alarm (uyarıdan sonra)",
    "answered after": "cevap süresi",
    "seizure?": "nöbet mi?",
    "strength": "şiddet",
    "remembers:": "hatırlıyor:",
    "recovery": "toparlanma",
    "felt:": "hissetti:",
    "medication:": "ilaç:",
    "before:": "öncesinde:",
    "Alert": "Uyarı", "Night": "Gece", "Test": "Deneme", "OK": "Tamam",

    // aftercare
    "Skip": "Atla",
    "How are you feeling?": "Nasıl hissediyorsun?",
    "Optional. Your answers go into your log for your doctor. Take your time.": "İsteğe bağlı. Cevapların doktorun için günlüğüne eklenir. Acele etme.",
    "Was it a seizure?": "Nöbet müydü?",
    "How strong did it feel?": "Ne kadar şiddetli hissettirdi?",
    "Do you remember it?": "Hatırlıyor musun?",
    "Right now I feel": "Şu an hissettiklerim",
    "Time until I felt like myself again": "Kendime gelmem ne kadar sürdü",
    "Before this, there was": "Bundan önce şunlar vardı",
    "My medication today": "Bugünkü ilaçlarım",
    "Anything else": "Başka bir şey",
    "Save to my log": "Günlüğüme kaydet",
    "I think so": "Sanırım evet", "No, false alarm": "Hayır, yanlış alarm", "Not sure": "Emin değilim",
    "1 mild": "1 hafif", "5 very strong": "5 çok şiddetli",
    "Yes": "Evet", "Partly": "Kısmen", "No": "Hayır",
    "Fine": "İyi", "Tired": "Yorgun", "Headache": "Baş ağrısı", "Confused": "Kafam karışık", "Muscle pain": "Kas ağrısı",
    "Bit my tongue": "Dilimi ısırdım", "Injured": "Yaralandım", "Wet the bed": "Altımı ıslattım", "Low mood": "Moralim bozuk",
    "Under 15 min": "15 dakikadan az", "15-60 min": "15-60 dakika", "1-3 hours": "1-3 saat", "More than 3 hours": "3 saatten fazla", "Not yet": "Henüz değil",
    "Missed medication": "İlacımı atladım", "Little sleep": "Az uyudum", "Alcohol": "Alkol",
    "Ill or fever": "Hastalık ya da ateş", "Flashing lights": "Yanıp sönen ışıklar", "Period": "Regl",
    "Taken on time": "Zamanında aldım", "Taken late": "Geç aldım", "Missed": "Atladım", "Rescue medicine used": "Kurtarma ilacı kullandım",

    // diary
    "Just for you. An entry goes into a doctor report only if you tick the box.": "Sadece senin için. Bir not, sadece kutuyu işaretlersen doktor raporuna girer.",
    "Today I feel": "Bugün kendimi şöyle hissediyorum",
    "Good": "İyi", "Okay": "Fena değil", "Low": "Düşük",
    "Hours of sleep last night": "Dün gece kaç saat uyudun",
    "Stress": "Stres", "Medium": "Orta", "High": "Yüksek",
    "Medication": "İlaç", "All taken": "Hepsini aldım", "Some missed": "Bazılarını atladım", "All missed": "Hepsini atladım",
    "Notes": "Notlar",
    "Include in doctor report": "Doktor raporuna ekle",
    "Save today's entry": "Bugünün notunu kaydet",
    "Earlier entries": "Önceki notlar",
    "No entries yet.": "Henüz not yok.",
    "(no notes)": "(not yok)",
    "Shared": "Paylaşılıyor", "Private": "Özel",
    "mood": "ruh hali", "h sleep": "saat uyku", "stress": "stres",

    // report
    "Report for your doctor": "Doktorun için rapor",
    "Last 7 days": "Son 7 gün", "Last 30 days": "Son 30 gün", "Last 90 days": "Son 90 gün",
    "Download spreadsheet (opens in Excel)": "Tabloyu indir (Excel'de açılır)",
    "Share with my doctor": "Doktorumla paylaş",
    "Sharing opens your email or messaging app. You choose what to send; nothing is sent automatically. The spreadsheet lists every event; the summary above goes in the message.":
      "Paylaşma, e-posta ya da mesaj uygulamanı açar. Neyin gönderileceğini sen seçersin; hiçbir şey otomatik gönderilmez. Tablo her olayı listeler; yukarıdaki özet mesaja eklenir.",
    "possible seizures detected": "olası nöbet tespit edildi",
    "times contacts were alerted": "kez yakınlara haber verildi",
    "auras reported": "aura bildirildi",
    "hours watched at night": "saat gece izlendi",

    // replay
    "A real seizure, replayed": "Gerçek bir nöbet, yeniden oynatılıyor",
    "Coming in the next version.": "Bir sonraki sürümde geliyor.",
    "This screen will play back a real night recorded in a hospital (SeizeIT2 dataset), from a patient the model never saw during training. You will see the movement signal, the moment the seizure starts, and the moment Beside raises the alarm.":
      "Bu ekran, hastanede kaydedilmiş gerçek bir geceyi (SeizeIT2 veri seti) yeniden oynatacak. Kayıt, modelin eğitim sırasında hiç görmediği bir hastaya ait. Hareket sinyalini, nöbetin başladığı anı ve Beside'ın alarm verdiği anı göreceksin.",

    // placeholders
    "Dr. ...": "Dr. ...",
    "for example: lighthouse": "örneğin: deniz feneri",
    "For example: woke up on the floor, felt different from usual": "Örneğin: yerde uyandım, her zamankinden farklı hissettim",
    "e.g. 7.5": "örn. 7.5",
    "Anything you want to remember about today": "Bugünle ilgili hatırlamak istediğin her şey"
  };

  const TABLES = { tr: TR };
  let lang = "en";

  function t(s) {
    const table = TABLES[lang];
    return table && Object.prototype.hasOwnProperty.call(table, s) ? table[s] : s;
  }
  function setLang(l) { lang = TABLES[l] ? l : "en"; document.documentElement.lang = lang; }
  function getLang() { return lang; }
  function detectLang() { return (navigator.language || "en").toLowerCase().startsWith("tr") ? "tr" : "en"; }

  // translate every static text node and placeholder; the English original is remembered on the node
  function translateDOM(rootEl) {
    const w = document.createTreeWalker(rootEl || document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const tag = n.parentElement && n.parentElement.tagName;
      if (tag === "SCRIPT" || tag === "STYLE") continue;
      if (n._en === undefined) {
        const raw = n.nodeValue, core = raw.trim();
        if (!core) continue;
        n._en = core; n._pre = raw.slice(0, raw.indexOf(core)); n._post = raw.slice(raw.indexOf(core) + core.length);
      }
      n.nodeValue = n._pre + t(n._en) + n._post;
    }
    (rootEl || document).querySelectorAll("[placeholder]").forEach(e => {
      if (e.dataset.enPh === undefined) e.dataset.enPh = e.placeholder;
      e.placeholder = t(e.dataset.enPh);
    });
  }

  root.i18n = { t, setLang, getLang, detectLang, translateDOM, languages: { en: "English", tr: "Türkçe" } };
})(window);
