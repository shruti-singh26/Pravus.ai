import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: {
        translation: {
          navigation: {
            back: 'Back',
          },
          language: 'Language',
          lightMode: 'Light Mode',
          darkMode: 'Dark Mode',
          productSearch: {
            welcome: 'Your Smart Manual Assistant',
            subtitle: 'Unlock the full potential of your devices with AI-powered manual assistance. Get instant answers, smart solutions, and expert guidance at your fingertips.',
            byCategory: 'Search by Category',
            selectCategory: 'Select category',
            features: 'Features'
          },
          categories: {
            tv_video: 'TV & Video',
            tv_video_desc: 'Smart TVs, Home Theater, Streaming Devices',
            audio: 'Audio',
            audio_desc: 'Speakers, Headphones, Sound Systems',
            mobile: 'Mobile Devices',
            mobile_desc: 'Smartphones, Tablets, Wearables',
            computers: 'Computers',
            computers_desc: 'Laptops, Desktops, Monitors, Accessories',
            home_appliances: 'Home Appliances',
            home_appliances_desc: 'Washing Machines, Dryers, Vacuum Cleaners',
            kitchen_appliances: 'Kitchen Appliances',
            kitchen_appliances_desc: 'Refrigerators, Microwaves, Dishwashers',
            climate: 'Climate Control',
            climate_desc: 'Air Conditioners, Air Purifiers, Fans',
            healthcare: 'Healthcare',
            healthcare_desc: 'Personal Care, Grooming, Health Monitoring',
            lighting: 'Lighting',
            lighting_desc: 'Smart Lights, Lamps, Light Fixtures',
            gaming: 'Gaming',
            gaming_desc: 'Gaming Consoles, Accessories',
            cameras: 'Cameras',
            cameras_desc: 'Digital Cameras, Security Cameras, Accessories',
            electronics: 'Other Electronics',
            electronics_desc: 'Various Electronic Devices and Accessories'
          },
          features: {
            easy_search: {
              title: 'Easy Search',
              description: 'Find the right manual quickly with our intuitive search system'
            },
            ai_assistant: {
              title: 'AI Assistant',
              description: 'Get instant answers to your questions with our intelligent chat system'
            },
            smart_solutions: {
              title: 'Smart Solutions',
              description: 'Receive personalized troubleshooting tips and recommendations'
            }
          },
          productDetails: {
            title: 'Product Details',
            availableManuals: 'Available Manuals',
            available: 'Available',
            unavailable: 'Unavailable',
            askIntelligent: 'Ask Intelligent AI',
            haveManual: 'Have a manual?',
            uploadInstructions: 'Upload your manual to get intelligent assistance',
            upload: 'Upload',
            uploading: 'Uploading...',
          },
          chat: {
            pdfViewer: 'Manual Viewer',
            pdfPlaceholder: 'PDF viewer will be displayed here',
            inputPlaceholder: 'Ask a question about the manual...',
            send: 'Send',
            helpful: 'This was helpful',
            notHelpful: 'This was not helpful',
            welcome: "Hi, I'm your Pravus.AI Assistant!",
            welcomeManual: "I'm here to help you get the most out of your {{brand}} {{model}}. Let me be your guide for:",
            welcomeGeneral: "I'm your dedicated product expert, ready to help you understand and get the most out of your electronic devices.",
            features: {
              title: "Product Features",
              understand: "Understanding all features and settings",
              performance: "Getting the best performance",
              discover: "Discovering hidden capabilities"
            },
            setup: {
              title: "Setup & Support",
              installation: "Easy installation guidance",
              configuration: "Step-by-step configuration",
              troubleshooting: "Quick troubleshooting"
            },
            maintenance: {
              title: "Tips & Care",
              practices: "Maintenance best practices",
              tips: "Optimization tips",
              safety: "Safety guidelines"
            },
            capabilities: {
              title: "I Can Help You With",
              features: "Complete product features guide",
              support: "Setup and installation support",
              troubleshooting: "Troubleshooting assistance",
              maintenance: "Maintenance and care tips"
            },
            assistPrompt: "How can I assist you today with your {{brand}} {{model}}?",
            generalPrompt: "How can I assist you today?"
          },
          search: 'Search',
        },
      },
      es: {
        translation: {
          navigation: {
            back: 'Volver',
          },
          language: 'Idioma',
          lightMode: 'Modo Claro',
          darkMode: 'Modo Oscuro',
          productSearch: {
            welcome: 'Tu Asistente Inteligente de Manuales',
            subtitle: 'Desbloquea todo el potencial de tus dispositivos con asistencia de manuales impulsada por IA. Obtén respuestas instantáneas, soluciones inteligentes y orientación experta al alcance de tu mano.',
            byCategory: 'Buscar por Categoría',
            selectCategory: 'Selecciona una categoría',
            features: 'Características'
          },
          categories: {
            tv_video: 'TV y Video',
            tv_video_desc: 'Smart TVs, Cine en Casa, Dispositivos de Streaming',
            audio: 'Audio',
            audio_desc: 'Altavoces, Auriculares, Sistemas de Sonido',
            mobile: 'Dispositivos Móviles',
            mobile_desc: 'Smartphones, Tablets, Dispositivos Portátiles',
            computers: 'Computadoras',
            computers_desc: 'Laptops, Computadoras de Escritorio, Monitores, Accesorios',
            home_appliances: 'Electrodomésticos',
            home_appliances_desc: 'Lavadoras, Secadoras, Aspiradoras',
            kitchen_appliances: 'Electrodomésticos de Cocina',
            kitchen_appliances_desc: 'Refrigeradores, Microondas, Lavavajillas',
            climate: 'Control de Clima',
            climate_desc: 'Aires Acondicionados, Purificadores de Aire, Ventiladores',
            healthcare: 'Salud',
            healthcare_desc: 'Cuidado Personal, Aseo, Monitoreo de Salud',
            lighting: 'Iluminación',
            lighting_desc: 'Luces Inteligentes, Lámparas, Accesorios de Iluminación',
            gaming: 'Videojuegos',
            gaming_desc: 'Consolas de Juegos, Accesorios',
            cameras: 'Cámaras',
            cameras_desc: 'Cámaras Digitales, Cámaras de Seguridad, Accesorios',
            electronics: 'Otros Electrónicos',
            electronics_desc: 'Varios Dispositivos Electrónicos y Accesorios'
          },
          features: {
            easy_search: {
              title: 'Búsqueda Fácil',
              description: 'Encuentra el manual correcto rápidamente con nuestro sistema de búsqueda intuitivo'
            },
            ai_assistant: {
              title: 'Asistente IA',
              description: 'Obtén respuestas instantáneas a tus preguntas con nuestro sistema de chat inteligente'
            },
            smart_solutions: {
              title: 'Soluciones Inteligentes',
              description: 'Recibe consejos de solución de problemas y recomendaciones personalizadas'
            }
          },
          productDetails: {
            title: 'Detalles del Producto',
            availableManuals: 'Manuales Disponibles',
            available: 'Disponible',
            unavailable: 'No Disponible',
            askIntelligent: 'Preguntar a la IA',
            haveManual: '¿Tienes un manual?',
            uploadInstructions: 'Sube tu manual para obtener asistencia inteligente',
            upload: 'Subir',
            uploading: 'Subiendo...',
          },
          chat: {
            pdfViewer: 'Visor de Manual',
            pdfPlaceholder: 'El visor PDF se mostrará aquí',
            inputPlaceholder: 'Haz una pregunta sobre el manual...',
            send: 'Enviar',
            helpful: 'Esto fue útil',
            notHelpful: 'Esto no fue útil',
            welcome: "¡Hola, soy tu Asistente Pravus.AI!",
            welcomeManual: "Estoy aquí para ayudarte a sacar el máximo provecho de tu {{brand}} {{model}}. Permíteme ser tu guía para:",
            welcomeGeneral: "Soy tu experto en productos dedicado, listo para ayudarte a entender y aprovechar al máximo tus dispositivos electrónicos.",
            features: {
              title: "Características del Producto",
              understand: "Comprensión de todas las características y configuraciones",
              performance: "Obtener el mejor rendimiento",
              discover: "Descubrir capacidades ocultas"
            },
            setup: {
              title: "Configuración y Soporte",
              installation: "Guía de instalación fácil",
              configuration: "Configuración paso a paso",
              troubleshooting: "Solución rápida de problemas"
            },
            maintenance: {
              title: "Consejos y Cuidados",
              practices: "Mejores prácticas de mantenimiento",
              tips: "Consejos de optimización",
              safety: "Pautas de seguridad"
            },
            capabilities: {
              title: "Puedo Ayudarte Con",
              features: "Guía completa de características del producto",
              support: "Soporte de configuración e instalación",
              troubleshooting: "Asistencia en resolución de problemas",
              maintenance: "Consejos de mantenimiento y cuidado"
            },
            assistPrompt: "¿Cómo puedo ayudarte hoy con tu {{brand}} {{model}}?",
            generalPrompt: "¿Cómo puedo ayudarte hoy?"
          },
          search: 'Buscar',
        },
      },
      hi: {
        translation: {
          navigation: {
            back: 'वापस',
          },
          language: 'भाषा',
          lightMode: 'लाइट मोड',
          darkMode: 'डार्क मोड',
          productSearch: {
            welcome: 'आपका स्मार्ट मैनुअल सहायक',
            subtitle: 'AI-संचालित मैनुअल सहायता के साथ अपने उपकरणों की पूरी क्षमता को अनलॉक करें। तुरंत उत्तर, स्मार्ट समाधान और विशेषज्ञ मार्गदर्शन प्राप्त करें।',
            byCategory: 'श्रेणी के अनुसार खोजें',
            selectCategory: 'श्रेणी चुनें',
            features: 'विशेषताएं'
          },
          categories: {
            tv_video: 'टीवी और वीडियो',
            tv_video_desc: 'स्मार्ट टीवी, होम थिएटर, स्ट्रीमिंग डिवाइस',
            audio: 'ऑडियो',
            audio_desc: 'स्पीकर, हेडफोन, साउंड सिस्टम',
            mobile: 'मोबाइल डिवाइस',
            mobile_desc: 'स्मार्टफोन, टैबलेट, वियरेबल्स',
            computers: 'कंप्यूटर',
            computers_desc: 'लैपटॉप, डेस्कटॉप, मॉनिटर, एक्सेसरीज',
            home_appliances: 'घरेलू उपकरण',
            home_appliances_desc: 'वॉशिंग मशीन, ड्रायर, वैक्यूम क्लीनर',
            kitchen_appliances: 'किचन उपकरण',
            kitchen_appliances_desc: 'रेफ्रिजरेटर, माइक्रोवेव, डिशवॉशर',
            climate: 'जलवायु नियंत्रण',
            climate_desc: 'एयर कंडीशनर, एयर प्यूरीफायर, पंखे',
            healthcare: 'स्वास्थ्य देखभाल',
            healthcare_desc: 'व्यक्तिगत देखभाल, ग्रूमिंग, स्वास्थ्य निगरानी',
            lighting: 'प्रकाश व्यवस्था',
            lighting_desc: 'स्मार्ट लाइट्स, लैंप, लाइटिंग फिक्स्चर',
            gaming: 'गेमिंग',
            gaming_desc: 'गेमिंग कंसोल, एक्सेसरीज',
            cameras: 'कैमरा',
            cameras_desc: 'डिजिटल कैमरा, सुरक्षा कैमरा, एक्सेसरीज',
            electronics: 'अन्य इलेक्ट्रॉनिक्स',
            electronics_desc: 'विभिन्न इलेक्ट्रॉनिक उपकरण और एक्सेसरीज'
          },
          features: {
            easy_search: {
              title: 'आसान खोज',
              description: 'हमारी सहज खोज प्रणाली के साथ सही मैनुअल तुरंत खोजें'
            },
            ai_assistant: {
              title: 'AI सहायक',
              description: 'हमारी इंटेलिजेंट चैट प्रणाली के साथ अपने प्रश्नों के तुरंत उत्तर प्राप्त करें'
            },
            smart_solutions: {
              title: 'स्मार्ट समाधान',
              description: 'व्यक्तिगत समस्या समाधान टिप्स और सिफारिशें प्राप्त करें'
            }
          },
          productDetails: {
            title: 'उत्पाद विवरण',
            availableManuals: 'उपलब्ध मैनुअल',
            available: 'उपलब्ध',
            unavailable: 'अनुपलब्ध',
            askIntelligent: 'AI से पूछें',
            haveManual: 'मैनुअल है?',
            uploadInstructions: 'इंटेलिजेंट सहायता प्राप्त करने के लिए अपना मैनुअल अपलोड करें',
            upload: 'अपलोड',
            uploading: 'अपलोड हो रहा है...',
          },
          chat: {
            pdfViewer: 'मैनुअल व्यूअर',
            pdfPlaceholder: 'पीडीएफ व्यूअर यहां दिखाया जाएगा',
            inputPlaceholder: 'मैनुअल के बारे में कोई प्रश्न पूछें...',
            send: 'भेजें',
            helpful: 'यह मददगार था',
            notHelpful: 'यह मददगार नहीं था',
            welcome: "नमस्ते, मैं आपका Pravus.AI सहायक हूं!",
            welcomeManual: "मैं आपको {{brand}} {{model}} का सर्वोत्तम उपयोग करने में मदद करने के लिए यहां हूं। मैं आपका मार्गदर्शक हूं:",
            welcomeGeneral: "मैं आपका समर्पित उत्पाद विशेषज्ञ हूं, आपके इलेक्ट्रॉनिक उपकरणों को समझने और उनका सर्वोत्तम उपयोग करने में मदद करने के लिए तैयार हूं।",
            features: {
              title: "उत्पाद विशेषताएं",
              understand: "सभी विशेषताओं और सेटिंग्स को समझना",
              performance: "सर्वोत्तम प्रदर्शन प्राप्त करना",
              discover: "छिपी हुई क्षमताओं की खोज"
            },
            setup: {
              title: "सेटअप और सहायता",
              installation: "आसान इंस्टॉलेशन मार्गदर्शन",
              configuration: "चरण-दर-चरण कॉन्फ़िगरेशन",
              troubleshooting: "त्वरित समस्या समाधान"
            },
            maintenance: {
              title: "टिप्स और देखभाल",
              practices: "रखरखाव के सर्वोत्तम तरीके",
              tips: "अनुकूलन के टिप्स",
              safety: "सुरक्षा दिशानिर्देश"
            },
            capabilities: {
              title: "मैं इनमें आपकी मदद कर सकता हूं",
              features: "उत्पाद विशेषताओं की पूर्ण गाइड",
              support: "सेटअप और इंस्टॉलेशन सहायता",
              troubleshooting: "समस्या समाधान सहायता",
              maintenance: "रखरखाव और देखभाल के टिप्स"
            },
            assistPrompt: "मैं आज आपके {{brand}} {{model}} के साथ कैसे मदद कर सकता हूं?",
            generalPrompt: "मैं आज आपकी कैसे मदद कर सकता हूं?"
          },
          search: 'खोज',
        },
      },
      pl: {
        translation: {
          navigation: {
            back: 'Wstecz',
          },
          language: 'Język',
          lightMode: 'Tryb jasny',
          darkMode: 'Tryb ciemny',
          productSearch: {
            welcome: 'Twój Inteligentny Asystent Instrukcji',
            subtitle: 'Odblokuj pełny potencjał swoich urządzeń dzięki asystentowi instrukcji obsługi wspieranemu przez AI. Otrzymuj natychmiastowe odpowiedzi, inteligentne rozwiązania i eksperckie wskazówki.',
            byCategory: 'Szukaj według kategorii',
            selectCategory: 'Wybierz kategorię',
            features: 'Funkcje'
          },
          categories: {
            tv_video: 'TV i Wideo',
            tv_video_desc: 'Smart TV, Kino domowe, Urządzenia streamingowe',
            audio: 'Audio',
            audio_desc: 'Głośniki, Słuchawki, Systemy dźwiękowe',
            mobile: 'Urządzenia mobilne',
            mobile_desc: 'Smartfony, Tablety, Urządzenia ubieralne',
            computers: 'Komputery',
            computers_desc: 'Laptopy, Komputery stacjonarne, Monitory, Akcesoria',
            home_appliances: 'Sprzęt AGD',
            home_appliances_desc: 'Pralki, Suszarki, Odkurzacze',
            kitchen_appliances: 'Sprzęt kuchenny',
            kitchen_appliances_desc: 'Lodówki, Mikrofalówki, Zmywarki',
            climate: 'Kontrola klimatu',
            climate_desc: 'Klimatyzatory, Oczyszczacze powietrza, Wentylatory',
            healthcare: 'Zdrowie',
            healthcare_desc: 'Pielęgnacja osobista, Urządzenia do monitorowania zdrowia',
            lighting: 'Oświetlenie',
            lighting_desc: 'Inteligentne oświetlenie, Lampy, Osprzęt oświetleniowy',
            gaming: 'Gaming',
            gaming_desc: 'Konsole do gier, Akcesoria',
            cameras: 'Aparaty',
            cameras_desc: 'Aparaty cyfrowe, Kamery bezpieczeństwa, Akcesoria',
            electronics: 'Pozostała elektronika',
            electronics_desc: 'Różne urządzenia elektroniczne i akcesoria'
          },
          features: {
            easy_search: {
              title: 'Łatwe wyszukiwanie',
              description: 'Szybko znajdź odpowiednią instrukcję dzięki naszemu intuicyjnemu systemowi wyszukiwania'
            },
            ai_assistant: {
              title: 'Asystent AI',
              description: 'Otrzymuj natychmiastowe odpowiedzi na swoje pytania dzięki naszemu inteligentnemu systemowi czatu'
            },
            smart_solutions: {
              title: 'Inteligentne rozwiązania',
              description: 'Otrzymuj spersonalizowane wskazówki i zalecenia dotyczące rozwiązywania problemów'
            }
          },
          productDetails: {
            title: 'Szczegóły produktu',
            availableManuals: 'Dostępne instrukcje',
            available: 'Dostępne',
            unavailable: 'Niedostępne',
            askIntelligent: 'Zapytaj AI',
            haveManual: 'Masz instrukcję?',
            uploadInstructions: 'Prześlij swoją instrukcję, aby uzyskać inteligentną pomoc',
            upload: 'Prześlij',
            uploading: 'Przesyłanie...',
          },
          chat: {
            pdfViewer: 'Przeglądarka instrukcji',
            pdfPlaceholder: 'Przeglądarka PDF zostanie wyświetlona tutaj',
            inputPlaceholder: 'Zadaj pytanie dotyczące instrukcji...',
            send: 'Wyślij',
            helpful: 'To było pomocne',
            notHelpful: 'To nie było pomocne',
            welcome: "Hi, I'm your Pravus.AI Assistant!",
            welcomeManual: "I'm here to help you get the most out of your {{brand}} {{model}}. Let me be your guide for:",
            welcomeGeneral: "I'm your dedicated product expert, ready to help you understand and get the most out of your electronic devices.",
            features: {
              title: "Product Features",
              understand: "Understanding all features and settings",
              performance: "Getting the best performance",
              discover: "Discovering hidden capabilities"
            },
            setup: {
              title: "Setup & Support",
              installation: "Easy installation guidance",
              configuration: "Step-by-step configuration",
              troubleshooting: "Quick troubleshooting"
            },
            maintenance: {
              title: "Tips & Care",
              practices: "Maintenance best practices",
              tips: "Optimization tips",
              safety: "Safety guidelines"
            },
            capabilities: {
              title: "I Can Help You With",
              features: "Complete product features guide",
              support: "Setup and installation support",
              troubleshooting: "Troubleshooting assistance",
              maintenance: "Maintenance and care tips"
            },
            assistPrompt: "How can I assist you today with your {{brand}} {{model}}?",
            generalPrompt: "How can I assist you today?"
          },
          search: 'Szukaj',
        },
      },
    },
  });

export default i18n; 