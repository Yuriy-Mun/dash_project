// Словарь для перевода месяцев
const monthTranslations = {
    'January': 'Январь',
    'February': 'Февраль',
    'March': 'Март',
    'April': 'Апрель',
    'May': 'Май',
    'June': 'Июнь',
    'July': 'Июль',
    'August': 'Август',
    'September': 'Сентябрь',
    'October': 'Октябрь',
    'November': 'Ноябрь',
    'December': 'Декабрь'
};

// Функция для локализации календаря
function localizeCalendar() {
    // Находим все заголовки месяцев
    const captions = document.querySelectorAll('.CalendarMonth_caption');
    
    captions.forEach(caption => {
        const monthYear = caption.textContent.trim().split(' ');
        const month = monthYear[0];
        const year = monthYear[1];
        
        if (monthTranslations[month]) {
            caption.setAttribute('data-month', `${monthTranslations[month]} ${year}`);
        }
    });
}

// Запускаем локализацию при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    localizeCalendar();
    
    // Наблюдаем за изменениями в DOM для динамической локализации
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                localizeCalendar();
            }
        });
    });
    
    // Начинаем наблюдение за изменениями в DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}); 