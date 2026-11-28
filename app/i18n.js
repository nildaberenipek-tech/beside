/* Beside translations. Keys are the English text. To add a language, add another table to TABLES.
   Stored data (log, diary) is kept in English and translated only for display. */
(function (root) {
  "use strict";

  const TR = {
    // splash
    "Always beside you": "Hep yanında",

    // consent
    "Before we start": "Başlamadan önce",
    "At night, Beside watches for the strong movements of a seizure and gets the people you choose to check on you. For that it needs a few permissions. You can turn them off later in your phone settings.":
      "Beside gece boyunca nöbetin güçlü hareketlerini izler ve seçtiğin kişilerin seni kontrol etmesini sağlar. Bunun için birkaç izne ihtiyacı var. İstersen bunları sonra telefonunun ayarlarından kapatabilirsin.",
    "Motion": "Hareket",
    "To notice the rhythmic jerking of a convulsive seizure while you sleep.": "Uyurken kasılmalı bir nöbetin ritmik sarsıntılarını fark etmek için.",
    "Location": "Konum",
    "Only sent in an emergency, so your people know where to come.": "Sadece acil durumda gönderilir, yakınların nereye geleceğini bilsin diye.",
    "Microphone": "Mikrofon",
    "Only when you turn on listening for your code word. Nothing is recorded.": "Sadece kod kelimeni dinlemeyi açtığında. Hiçbir şey kaydedilmez.",
    "Your log": "Kayıtların",
    "Kept on this phone. It only leaves when you share a report.": "Bu telefonda kalır. Sadece sen bir rapor paylaşırsan dışarı çıkar.",
    "Beside is a research prototype, not a medical device.": "Beside bir araştırma prototipidir, tıbbi cihaz değildir.",
    "It can miss seizures and it can raise false alarms. Keep following your doctor's advice.": "Nöbetleri kaçırabilir ve yanlış alarm verebilir. Doktorunun önerilerine uymaya devam et.",
    "I understand, continue": "Anladım, devam et",

    // settings
    "Done": "Bitti",
    "Your safety plan": "Güvenlik planın",
    "Saved on this phone only.": "Sadece bu telefonda saklanır.",
    "Language": "Dil",
    "About you": "Senin hakkında",
    "Your name": "Adın",
    "Used in your emergency message": "Acil durum mesajında kullanılır",
    "Home address (optional)": "Ev adresi (isteğe bağlı)",
    "So help can find you": "Yardım seni bulabilsin diye",
    "From your doctor": "Doktorundan",
    "Seizure type": "Nöbet türü",
    "Tonic-clonic (including focal to bilateral)": "Tonik-klonik (fokalden iki taraflıya dönüşen dahil)",
    "Focal with movement": "Hareketli fokal",
    "Focal without movement": "Hareketsiz fokal",
    "Usual seizure length (seconds)": "Nöbetlerin genelde kaç saniye sürüyor",
    "Sound can trigger my seizures": "Nöbetlerim sesle tetiklenebiliyor",
    "If ticked, Beside will not speak out loud during an alert.": "İşaretliyse Beside acil durumda sesli konuşmaz.",
    "Doctor's name": "Doktorunun adı",
    "Doctor's email for reports": "Raporlar için doktorunun e-postası",
    "Your doctor only gets the reports you share. Emergency alerts go to your people, because a doctor may not see a message at night.":
      "Doktoruna sadece senin paylaştığın raporlar gider. Acil uyarılar yakınlarına gider, çünkü doktor gece mesajı göremeyebilir.",
    "People to contact": "Haber verilecek kişiler",
    "Name": "Ad",
    "Phone": "Telefon",
    "Remove": "Sil",
    "Add a person": "Kişi ekle",
    "Message app": "Mesaj uygulaması",
    "Emergency number": "Acil numara",
    "Automatic alerts": "Otomatik uyarılar",
    "Alert my people automatically": "Yakınlarıma otomatik haber ver",
    "Uses the free ntfy app on their phone. No need to tap Send.": "Onların telefonundaki ücretsiz ntfy uygulamasını kullanır. Gönder'e basmak gerekmez.",
    "On their phone, install": "Onların telefonuna",
    "(App Store or Google Play).": "uygulamasını kur (App Store ya da Google Play).",
    "Tap": "",
    "and enter this family code:": "simgesine dokun ve bu aile kodunu yaz:",
    "Send a test alert": "Deneme uyarısı gönder",
    "Alerts pass through the ntfy.sh service. Anyone with the code can read them, so only share it with your people.":
      "Uyarılar ntfy.sh servisinden geçer. Kodu bilen herkes okuyabilir, bu yüzden kodu sadece yakınlarınla paylaş.",
    "Sending...": "Gönderiliyor...",
    "Sent. Check their phone.": "Gönderildi. Onların telefonuna bak.",
    "Could not send. Check the internet connection.": "Gönderilemedi. İnternet bağlantısını kontrol et.",
    "Beside test": "Beside deneme",
    "This is a test from Beside. If you can read it, alerts work.": "Bu Beside'dan bir deneme. Bunu okuyabiliyorsan uyarılar çalışıyor.",
    "Timing": "Süreler",
    "\"Are you OK?\" time after a possible seizure": "Olası nöbetten sonra \"İyi misin?\" süresi",
    "\"Are you OK?\" time after an aura": "Auradan sonra \"İyi misin?\" süresi",
    "10 seconds": "10 saniye", "15 seconds": "15 saniye", "20 seconds": "20 saniye", "30 seconds": "30 saniye",
    "45 seconds": "45 saniye", "60 seconds": "60 saniye", "90 seconds": "90 saniye", "2 minutes": "2 dakika",
    "Aura": "Aura",
    "Your code word": "Kod kelimen",
    "for example: lighthouse": "örneğin: deniz feneri",
    "Say it when you feel an aura. It tells your people and starts a check-in. It never calls an ambulance on its own.":
      "Aura hissettiğinde söyle. Yakınlarına haber verir ve kontrolü başlatır. Kendi başına asla ambulans çağırmaz.",
    "Use it with the phone locked (Siri)": "Telefon kilitliyken kullan (Siri)",
    "Open the": "",
    "app, then tap": "uygulamasını aç, sonra",
    "to make a new shortcut.": "simgesine dokunarak yeni bir kısayol oluştur.",
    "Add": "Ekle:",
    ". URL:": ". URL:",
    ". Method: POST. Body: text \"Aura reported\".": ". Yöntem: POST. Gövde: \"Aura bildirildi\" metni.",
    "to your contact with the text \"I feel an aura, please check on me\".": "ile yakınına \"Aura hissediyorum, lütfen beni kontrol et\" mesajı.",
    "Name the shortcut with your code word, then try it: lock the phone and say \"Hey Siri,": "Kısayola kod kelimenin adını ver ve dene: telefonu kilitle ve \"Hey Siri,",
    "your code word": "kod kelimen",
    "Use it with the phone locked (Samsung and Android)": "Telefon kilitliyken kullan (Samsung ve Android)",
    "Samsung: open": "Samsung:",
    "or": "ya da",
    "and make a routine started by a voice command.": "uygulamasını aç ve sesli komutla başlayan bir rutin oluştur.",
    "Other Android phones: in the": "Diğer Android telefonlar:",
    "app, create a routine with your code word.": "uygulamasında kod kelimenle bir rutin oluştur.",
    "Make the routine send a message to your contact.": "Rutin yakınına bir mesaj göndersin.",
    "Emergency buttons on your phone": "Telefonundaki acil durum tuşları",
    "iPhone:": "iPhone:",
    "Settings → Emergency SOS. Pressing the side button 5 times calls emergency services and texts your emergency contacts.":
      "Ayarlar → Acil SOS. Yan tuşa 5 kez basınca acil servis aranır ve acil durum kişilerine mesaj gider.",
    "Samsung:": "Samsung:",
    "Settings → Safety and emergency → Emergency SOS. Pressing the side key several times sends your location to your contacts.":
      "Ayarlar → Güvenlik ve acil durum → Acil SOS. Yan tuşa art arda basınca konumun kişilerine gönderilir.",
    "Display": "Ekran",
    "Calm display": "Sakin ekran",
    "Dims the app and turns off all animation. Beside never flashes.": "Uygulamayı kısar ve tüm animasyonları kapatır. Beside asla yanıp sönmez.",
    "Save": "Kaydet",
    "Research prototype. Not a medical device.": "Araştırma prototipi. Tıbbi cihaz değildir.",

    // home
    "Settings": "Ayarlar",
    "Good morning": "Günaydın", "Good afternoon": "İyi günler", "Good evening": "İyi akşamlar",
    "Sleep mode is off": "Uyku modu kapalı",
    "Sleep mode is on": "Uyku modu açık",
    "Add a person in Settings.": "Ayarlar'dan bir kişi ekle.",
    "Monthly report": "Aylık rapor",
    "Share the last 30 days with your doctor.": "Son 30 günü doktorunla paylaş.",
    "Open report": "Raporu aç",
    "Start sleep mode": "Uyku modunu başlat",
    "I feel an aura": "Aura hissediyorum",
    "Tell my people now": "Yakınlarıma hemen haber ver",
    "My diary": "Günlüğüm",
    "Daily notes": "Günlük notlar",
    "Seizure log": "Nöbet kaydı",
    "Every alarm and check-in": "Tüm alarmlar ve kontroller",
    "Doctor report": "Doktor raporu",
    "Summary and spreadsheet": "Özet ve tablo",
    "Real recording": "Gerçek kayıt",
    "Watch a real seizure being detected": "Gerçek bir nöbetin yakalanışını izle",
    "Practice": "Deneme",
    "Try the check-in": "Kontrolü dene",

    // sleep
    "Watching quietly. Sleep well.": "Sessizce izliyor. İyi uykular.",
    "Movement": "Hareket",
    "Keep the phone charging and the volume up. The screen stays on but dark.": "Telefonu şarjda tut ve sesini açık bırak. Ekran açık ama karanlık kalır.",
    "This browser cannot keep the screen on. Set Auto-Lock to Never tonight and keep the phone charging.":
      "Bu tarayıcı ekranı açık tutamıyor. Bu gece Otomatik Kilit'i \"Hiçbir Zaman\" yap ve telefonu şarjda tut.",
    "Starting...": "Başlıyor...",
    "The detection model did not load. Only the simulate button works.": "Tespit modeli yüklenemedi. Sadece taklit butonu çalışır.",
    "Demo mode": "Demo modu",
    "For showing the app: it alarms at a 50% score, so shaking the phone can set it off. Not for real use.":
      "Uygulamayı göstermek için: %50 skorda alarm verir, böylece telefonu sallamak alarmı başlatabilir. Gerçek kullanım için değil.",
    "Simulate a seizure": "Nöbet taklidi",
    "I'm awake, stop": "Uyandım, durdur",

    // aura, countdown, alert
    "Aura reported": "Aura bildirildi",
    "Are you OK?": "İyi misin?",
    "If you don't answer, your people will be alerted.": "Cevap vermezsen yakınlarına haber verilecek.",
    "Your people know about the aura. Tap below if you are fine.": "Yakınların aurayı biliyor. İyiysen aşağıya dokun.",
    "I'm OK": "İyiyim",
    "Beside: all OK": "Beside: her şey yolunda",
    "Getting help": "Yardım isteniyor",
    "Practice: this is what would happen": "Deneme: gerçekte bu olurdu",
    "Message to your people": "Yakınlarına giden mesaj",
    "If you call, you can say": "Ararsan şunu söyleyebilirsin",
    "I'm OK, it was a false alarm": "İyiyim, yanlış alarmdı",
    "Your people were alerted automatically.": "Yakınlarına otomatik olarak haber verildi.",
    "Opening your message app...": "Mesaj uygulaman açılıyor...",
    "unknown": "bilinmiyor",

    // log
    "Back": "Geri",
    "Every alarm and check-in, for you and your doctor.": "Senin ve doktorun için tüm alarmlar ve kontroller.",
    "Nothing yet.": "Henüz bir şey yok.",
    "Sleep mode": "Uyku modu",
    "Practice check-in": "Deneme kontrolü",
    "Check-in (demo)": "Kontrol (demo)",
    "Possible seizure detected": "Olası nöbet algılandı",
    "no answer yet": "henüz cevap yok",
    "answered: I'm OK": "cevap: iyiyim",
    "people alerted": "yakınlara haber verildi",
    "false alarm (after alert)": "yanlış alarm (haber verildikten sonra)",
    "practice finished": "deneme tamamlandı",
    "answered after": "cevap süresi",
    "seizure?": "nöbet mi?",
    "strength": "şiddet",
    "remembers:": "hatırlıyor:",
    "recovery": "toparlanma",
    "felt:": "hissetti:",
    "medication:": "ilaç:",
    "before:": "öncesinde:",
    "Alert": "Uyarı", "Night": "Gece", "OK": "Tamam",

    // aftercare
    "Skip": "Atla",
    "How are you feeling?": "Nasıl hissediyorsun?",
    "Only if you feel up to it. Your answers go into your log.": "Sadece kendini hazır hissedersen. Cevapların kaydına eklenir.",
    "Was it a seizure?": "Nöbet müydü?",
    "How strong was it?": "Ne kadar şiddetliydi?",
    "Do you remember it?": "Hatırlıyor musun?",
    "Right now I feel": "Şu an hissettiklerim",
    "Time until I felt like myself again": "Kendime gelmem ne kadar sürdü",
    "Before it happened": "Olmadan önce",
    "My medication today": "Bugünkü ilaçlarım",
    "Anything else": "Başka bir şey",
    "For example: woke up on the floor": "Örneğin: yerde uyandım",
    "Save to my log": "Kaydıma ekle",
    "I think so": "Sanırım evet", "No, false alarm": "Hayır, yanlış alarm", "Not sure": "Emin değilim",
    "1 mild": "1 hafif", "5 very strong": "5 çok şiddetli",
    "Yes": "Evet", "Partly": "Kısmen", "No": "Hayır",
    "Fine": "İyiyim", "Tired": "Yorgun", "Sleepy": "Uykulu", "Headache": "Baş ağrısı", "Confused": "Kafam karışık",
    "Memory gaps": "Hafıza boşlukları", "Trouble speaking": "Konuşmakta zorlanıyorum", "Muscle pain": "Kas ağrısı",
    "Weak on one side": "Bir tarafım güçsüz", "Numbness or tingling": "Uyuşma ya da karıncalanma", "Dizzy": "Başım dönüyor",
    "Nausea": "Mide bulantısı", "Blurred vision": "Bulanık görme", "Bit my tongue": "Dilimi ısırdım", "Injured": "Yaralandım",
    "Wet the bed": "Altımı ıslattım", "Scared or anxious": "Korkmuş ya da kaygılı", "Low mood": "Moralim bozuk",
    "Under 15 min": "15 dakikadan az", "15-60 min": "15-60 dakika", "1-3 hours": "1-3 saat", "More than 3 hours": "3 saatten fazla", "Not yet": "Henüz değil",
    "Missed medication": "İlacımı atladım", "Little sleep": "Az uyudum", "Stress": "Stres", "Alcohol": "Alkol",
    "Ill or fever": "Hastalık ya da ateş", "Flashing lights": "Yanıp sönen ışıklar", "Menstrual period": "Regl dönemi", "Skipped a meal": "Öğün atladım",
    "Taken on time": "Zamanında aldım", "Taken late": "Geç aldım", "Missed": "Atladım", "Rescue medicine used": "Acil ilacımı kullandım",

    // diary
    "Private. A note only goes to your doctor if you choose.": "Sadece senin için. Bir not, sadece sen istersen doktoruna gider.",
    "+ New note": "+ Yeni not",
    "in report": "raporda",
    "stress": "stres",
    "I feel": "Kendimi hissediyorum",
    "Great": "Çok iyi", "Good": "İyi", "Okay": "Fena değil", "Low": "Moralsiz", "Anxious": "Kaygılı", "Irritable": "Sinirli", "Unwell": "İyi değilim",
    "Hours of sleep last night": "Dün gece kaç saat uyudun",
    "e.g. 7.5": "örn. 7.5",
    "Medication": "İlaç",
    "All taken": "Hepsini aldım", "Some missed": "Bazılarını atladım", "All missed": "Hepsini atladım",
    "Note": "Not",
    "Anything you want to remember about today": "Bugünle ilgili hatırlamak istediğin her şey",
    "Add to doctor report": "Doktor raporuna ekle",
    "Only feelings and stress": "Sadece his ve stres",
    "Everything, including my note": "Notum dahil her şey",
    "Delete": "Sil",
    "No stress, calm": "Hiç stres yok, sakinim",
    "Very slight": "Çok hafif",
    "Slight, relaxed": "Hafif, rahatım",
    "A little tense": "Biraz gerginim",
    "Noticeably tense": "Fark edilir derecede gerginim",
    "Moderate, coping": "Orta, idare ediyorum",
    "Quite stressed": "Epey stresliyim",
    "Very stressed": "Çok stresliyim",
    "Hard to focus": "Odaklanmakta zorlanıyorum",
    "Overwhelmed": "Bunaldım",
    "Unbearable": "Dayanılmaz",
    "Diary": "Günlük",

    // report
    "Report for your doctor": "Doktorun için rapor",
    "Time range": "Zaman aralığı",
    "Last 7 days": "Son 7 gün", "Last 30 days": "Son 30 gün", "Last 90 days": "Son 90 gün",
    "Download spreadsheet (Excel)": "Tabloyu indir (Excel)",
    "Send to my doctor": "Doktoruma gönder",
    "Opens your email or messages so you can check it before sending.": "Göndermeden önce kontrol edebilmen için e-postanı ya da mesajlarını açar.",
    "possible seizure alarms": "olası nöbet alarmı",
    "times people were alerted": "kez yakınlara haber verildi",
    "auras reported": "aura bildirildi",
    "hours watched at night": "saat gece izlendi",

    // replay
    "A real seizure, replayed": "Gerçek bir nöbet, yeniden oynatılıyor",
    "This is a real night recorded in a hospital. Press play to watch Beside's detector go through it, the same code that runs on your phone. You will see the seizure start and the moment Beside would raise the alarm.":
      "Bu, hastanede kaydedilmiş gerçek bir gece. Oynat'a basınca Beside'ın dedektörünün, yani telefonunda çalışan kodun aynısının, bu geceyi nasıl izlediğini göreceksin. Nöbetin başladığı anı ve Beside'ın alarm vereceği anı göreceksin.",
    "Movement (sensor on the chest)": "Hareket (göğüsteki sensör)",
    "Seizure score (dashed line: alarm level)": "Nöbet skoru (kesikli çizgi: alarm seviyesi)",
    "Press play. The night plays 20 times faster than real time.": "Oynat'a bas. Gece, gerçek zamandan 20 kat hızlı oynar.",
    "Play": "Oynat", "Pause": "Duraklat", "Play again": "Tekrar oynat", "Speed": "Hız", "Speed 20x": "Hız 20x",
    "Shaded area: the seizure, as marked by doctors from video and EEG.": "Gölgeli alan: doktorların video ve EEG'ye bakarak işaretlediği nöbet.",
    "This patient was part of the training data, so this shows how the app behaves, not how accurate it is. Accuracy on new patients is in the README.":
      "Bu hasta eğitim verisindeydi. Bu yüzden bu ekran uygulamanın nasıl davrandığını gösterir, ne kadar doğru olduğunu değil. Yeni hastalardaki doğruluk README'de.",
    "The model never saw this patient during training.": "Model bu hastayı eğitimde hiç görmedi.",
    "Could not load the recording.": "Kayıt yüklenemedi.",
    "A false alarm went off before the seizure.": "Nöbetten önce bir yanlış alarm çaldı.",
    "The seizure has started. The detector is watching...": "Nöbet başladı. Dedektör izliyor...",

    "Dr. ...": "Dr. ..."
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

  // translate static text nodes and placeholders; the English original is remembered on each node
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
  // for tests: which visible English strings have no translation
  function missing(l) {
    const table = TABLES[l] || {}, out = new Set(), values = new Set(Object.values(table));
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const tag = n.parentElement && n.parentElement.tagName;
      if (tag === "SCRIPT" || tag === "STYLE") continue;
      const s = n._en !== undefined ? n._en : n.nodeValue.trim();
      const shown = n.nodeValue.trim();
      // untranslated = still showing an English source text that has no entry in the table
      if (s && shown === s && !(s in table) && !values.has(s) && /[a-z]{3}/i.test(s)) out.add(s);
    }
    document.querySelectorAll("[placeholder]").forEach(e => { const s = e.dataset.enPh || e.placeholder; if (s && !(s in table) && !values.has(s)) out.add(s); });
    return [...out];
  }

  root.i18n = { t, setLang, getLang, detectLang, translateDOM, missing };
})(window);
