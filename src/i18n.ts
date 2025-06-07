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
            chatButton: 'Chat with AI Assistant',
            demoButton: 'Try Demo Chat'
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
          admin: {
            title: 'Admin Panel',
            subtitle: 'Manual upload and management system',
            uploadTab: 'Upload Manual',
            manageTab: 'Manage Manuals',
            selectFile: 'Select File',
            productInformation: 'Product Information',
            brandPlaceholder: 'Enter manufacturer name (e.g., Samsung, LG)',
            modelPlaceholder: 'Enter model number or name (e.g., QN65Q70A)',
            yearPlaceholder: 'Enter manufacturing year',
            selectProductType: 'Select product type',
            uploadedManuals: 'Uploaded Manuals',
            brand: 'Brand',
            model: 'Model',
            year: 'Year',
            language: 'Language',
            unknown: 'Unknown',
            dropzone: {
              title: 'Drop your file here or click to browse',
              subtitle: 'Supported formats: PDF, TXT, DOC, DOCX (Max 16MB)',
              fileSelected: 'File Selected'
            },
            table: {
              fileName: 'File Name',
              brand: 'Brand',
              model: 'Model',
              type: 'Type',
              year: 'Year',
              language: 'Language',
              uploadDate: 'Upload Date',
              actions: 'Actions',
              unknown: 'Unknown'
            },
            noManuals: {
              title: 'No manuals uploaded yet',
              subtitle: 'Upload your first manual using the Upload tab'
            },
            uploadStatus: {
              processing: 'Processing manual...',
              pleaseWait: 'Please wait while we process your file',
              largeFileWarning: 'Large files may take several minutes to process',
              success: 'Manual successfully uploaded',
              error: 'Failed to upload manual',
              validationError: 'Please fill in all required fields'
            },
            confirmDeletion: {
              title: 'Confirm Deletion',
              text: 'Are you sure you want to delete this manual? This action cannot be undone.',
              cancel: 'Cancel',
              confirm: 'Delete',
              deleting: 'Deleting...'
            },
            actions: {
              upload: 'Upload Manual',
              processing: 'Processing...',
              refresh: 'Refresh List',
              delete: 'Delete',
              download: 'Download',
              view: 'View'
            },
            errors: {
              failedToLoad: 'Failed to load manuals',
              requestTimeout: 'Request timed out',
              connectionError: 'Cannot connect to server',
              uploadFailed: 'Upload failed',
              deleteFailed: 'Delete failed',
              downloadFailed: 'Download failed'
            }
          },
          manualScreen: {
            noManuals: {
              title: 'No manuals available yet',
              subtitle: 'Our manual database is being updated. Please check back soon.'
            },
            details: {
              year: 'Year',
              language: 'Language',
              demo: 'Demo',
              demoText: 'Sample data for demonstration'
            }
          }
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
            askIntelligent: 'Preguntar a la IA Inteligente',
            haveManual: '¿Tienes un manual?',
            uploadInstructions: 'Sube tu manual para obtener asistencia inteligente',
            upload: 'Subir',
            uploading: 'Subiendo...',
            chatButton: 'Chatear con Asistente IA',
            demoButton: 'Probar Chat Demo'
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
          admin: {
            title: 'Panel de Administración',
            subtitle: 'Sistema de carga y gestión de manuales',
            uploadTab: 'Subir Manual',
            manageTab: 'Gestionar Manuales',
            selectFile: 'Seleccionar Archivo',
            productInformation: 'Información del Producto',
            brandPlaceholder: 'Ingrese nombre del fabricante (ej. Samsung, LG)',
            modelPlaceholder: 'Ingrese número o nombre del modelo (ej. QN65Q70A)',
            yearPlaceholder: 'Ingrese año de fabricación',
            selectProductType: 'Seleccione tipo de producto',
            uploadedManuals: 'Manuales Subidos',
            brand: 'Marca',
            model: 'Modelo',
            year: 'Año',
            language: 'Idioma',
            unknown: 'Desconocido',
            dropzone: {
              title: 'Arrastra tu archivo aquí o haz clic para buscar',
              subtitle: 'Formatos soportados: PDF, TXT, DOC, DOCX (Máx 16MB)',
              fileSelected: 'Archivo Seleccionado'
            },
            table: {
              fileName: 'Nombre del Archivo',
              brand: 'Marca',
              model: 'Modelo',
              type: 'Tipo',
              year: 'Año',
              language: 'Idioma',
              uploadDate: 'Fecha de Subida',
              actions: 'Acciones',
              unknown: 'Desconocido'
            },
            noManuals: {
              title: 'Aún no hay manuales subidos',
              subtitle: 'Sube tu primer manual usando la pestaña de Subir'
            },
            uploadStatus: {
              processing: 'Procesando manual...',
              pleaseWait: 'Por favor espera mientras procesamos tu archivo',
              largeFileWarning: 'Los archivos grandes pueden tardar varios minutos en procesarse',
              success: 'Manual subido exitosamente',
              error: 'Error al subir el manual',
              validationError: 'Por favor completa todos los campos requeridos'
            },
            confirmDeletion: {
              title: 'Confirmar Eliminación',
              text: '¿Estás seguro de que deseas eliminar este manual? Esta acción no se puede deshacer.',
              cancel: 'Cancelar',
              confirm: 'Eliminar',
              deleting: 'Eliminando...'
            },
            actions: {
              upload: 'Subir Manual',
              processing: 'Procesando...',
              refresh: 'Actualizar Lista',
              delete: 'Eliminar',
              download: 'Descargar',
              view: 'Ver'
            },
            errors: {
              failedToLoad: 'Error al cargar los manuales',
              requestTimeout: 'La solicitud expiró',
              connectionError: 'No se puede conectar al servidor',
              uploadFailed: 'Error al subir',
              deleteFailed: 'Error al eliminar',
              downloadFailed: 'Error al descargar'
            }
          },
          manualScreen: {
            noManuals: {
              title: 'Aún no hay manuales disponibles',
              subtitle: 'Nuestra base de datos de manuales está siendo actualizada. Por favor, vuelve pronto.'
            },
            details: {
              year: 'Año',
              language: 'Idioma',
              demo: 'Demo',
              demoText: 'Datos de muestra para demostración'
            }
          }
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
            askIntelligent: 'Zapytaj Inteligentną AI',
            haveManual: 'Masz instrukcję?',
            uploadInstructions: 'Prześlij swoją instrukcję, aby uzyskać inteligentną pomoc',
            upload: 'Prześlij',
            uploading: 'Przesyłanie...',
            chatButton: 'Czatuj z Asystentem AI',
            demoButton: 'Wypróbuj Demo Czatu'
          },
          chat: {
            pdfViewer: 'Przeglądarka instrukcji',
            pdfPlaceholder: 'Przeglądarka PDF zostanie wyświetlona tutaj',
            inputPlaceholder: 'Zadaj pytanie dotyczące instrukcji...',
            send: 'Wyślij',
            helpful: 'To było pomocne',
            notHelpful: 'To nie było pomocne',
            welcome: "Cześć, jestem Twoim Asystentem Pravus.AI!",
            welcomeManual: "Jestem tutaj, aby pomóc Ci jak najlepiej wykorzystać Twój {{brand}} {{model}}. Pozwól, że będę Twoim przewodnikiem w:",
            welcomeGeneral: "Jestem Twoim dedykowanym ekspertem od produktów, gotowym pomóc Ci zrozumieć i w pełni wykorzystać Twoje urządzenia elektroniczne.",
            features: {
              title: "Funkcje Produktu",
              understand: "Zrozumienie wszystkich funkcji i ustawień",
              performance: "Uzyskanie najlepszej wydajności",
              discover: "Odkrywanie ukrytych możliwości"
            },
            setup: {
              title: "Konfiguracja i Wsparcie",
              installation: "Łatwe wskazówki instalacji",
              configuration: "Konfiguracja krok po kroku",
              troubleshooting: "Szybkie rozwiązywanie problemów"
            },
            maintenance: {
              title: "Wskazówki i Pielęgnacja",
              practices: "Najlepsze praktyki konserwacji",
              tips: "Wskazówki dotyczące optymalizacji",
              safety: "Wytyczne bezpieczeństwa"
            },
            capabilities: {
              title: "Mogę Pomóc Ci Z",
              features: "Kompletny przewodnik po funkcjach produktu",
              support: "Wsparcie w konfiguracji i instalacji",
              troubleshooting: "Pomoc w rozwiązywaniu problemów",
              maintenance: "Wskazówki dotyczące konserwacji i pielęgnacji"
            },
            assistPrompt: "Jak mogę Ci dziś pomóc z Twoim {{brand}} {{model}}?",
            generalPrompt: "Jak mogę Ci dziś pomóc?"
          },
          search: 'Szukaj',
          admin: {
            title: 'Panel Administratora',
            subtitle: 'System przesyłania i zarządzania instrukcjami',
            uploadTab: 'Prześlij Instrukcję',
            manageTab: 'Zarządzaj Instrukcjami',
            selectFile: 'Wybierz Plik',
            productInformation: 'Informacje o Produkcie',
            brandPlaceholder: 'Wprowadź nazwę producenta (np. Samsung, LG)',
            modelPlaceholder: 'Wprowadź numer lub nazwę modelu (np. QN65Q70A)',
            yearPlaceholder: 'Wprowadź rok produkcji',
            selectProductType: 'Wybierz typ produktu',
            uploadedManuals: 'Przesłane Instrukcje',
            brand: 'Marka',
            model: 'Model',
            year: 'Rok',
            language: 'Język',
            unknown: 'Nieznany',
            dropzone: {
              title: 'Przeciągnij plik tutaj lub kliknij, aby przeglądać',
              subtitle: 'Obsługiwane formaty: PDF, TXT, DOC, DOCX (Maks. 16MB)',
              fileSelected: 'Plik Wybrany'
            },
            table: {
              fileName: 'Nazwa Pliku',
              brand: 'Marka',
              model: 'Model',
              type: 'Typ',
              year: 'Rok',
              language: 'Język',
              uploadDate: 'Data Przesłania',
              actions: 'Akcje',
              unknown: 'Nieznany'
            },
            noManuals: {
              title: 'Brak przesłanych instrukcji',
              subtitle: 'Prześlij swoją pierwszą instrukcję używając zakładki Prześlij'
            },
            uploadStatus: {
              processing: 'Przetwarzanie instrukcji...',
              pleaseWait: 'Proszę czekać, trwa przetwarzanie pliku',
              largeFileWarning: 'Przetwarzanie dużych plików może potrwać kilka minut',
              success: 'Instrukcja została pomyślnie przesłana',
              error: 'Błąd podczas przesyłania instrukcji',
              validationError: 'Proszę wypełnić wszystkie wymagane pola'
            },
            confirmDeletion: {
              title: 'Potwierdź Usunięcie',
              text: 'Czy na pewno chcesz usunąć tę instrukcję? Tej operacji nie można cofnąć.',
              cancel: 'Anuluj',
              confirm: 'Usuń',
              deleting: 'Usuwanie...'
            },
            actions: {
              upload: 'Prześlij Instrukcję',
              processing: 'Przetwarzanie...',
              refresh: 'Odśwież Listę',
              delete: 'Usuń',
              download: 'Pobierz',
              view: 'Wyświetl'
            },
            errors: {
              failedToLoad: 'Nie udało się załadować instrukcji',
              requestTimeout: 'Przekroczono limit czasu żądania',
              connectionError: 'Nie można połączyć się z serwerem',
              uploadFailed: 'Przesyłanie nie powiodło się',
              deleteFailed: 'Usuwanie nie powiodło się',
              downloadFailed: 'Pobieranie nie powiodło się'
            }
          },
          manualScreen: {
            noManuals: {
              title: 'Brak dostępnych instrukcji',
              subtitle: 'Nasza baza instrukcji jest aktualizowana. Sprawdź ponownie wkrótce.'
            },
            details: {
              year: 'Rok',
              language: 'Język',
              demo: 'Demo',
              demoText: 'Przykładowe dane do demonstracji'
            }
          }
        },
      },
    },
  });

export default i18n; 