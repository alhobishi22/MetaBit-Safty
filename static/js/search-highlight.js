/**
 * دالة لإبراز كلمات البحث في نتائج البحث
 * تقوم بتغيير لون النص المطابق لكلمات البحث
 */
document.addEventListener('DOMContentLoaded', function() {
    // الحصول على استعلام البحث من عنوان URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    
    // إذا لم يكن هناك استعلام بحث، فلا داعي للاستمرار
    if (!searchQuery || searchQuery.trim() === '') {
        return;
    }
    
    // تقسيم استعلام البحث إلى كلمات فردية (بتجاهل الفراغات الزائدة)
    const searchTerms = searchQuery.trim().split(/\s+/).filter(term => term.length > 0);
    
    // تحسين التعبير العادي للبحث - تجنب استخدام حدود الكلمات للأرقام
    const isNumericSearch = searchTerms.every(term => /^\d+$/.test(term));
    
    // إنشاء نمط للبحث عن كل الكلمات
    let searchPattern;
    if (isNumericSearch) {
        // إذا كان البحث عن أرقام فقط، نستخدم تعبير عادي بسيط بدون حدود الكلمات
        searchPattern = new RegExp('(' + searchTerms.map(term => 
            term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // هروب من الأحرف الخاصة
        ).join('|') + ')', 'g');
    } else {
        // للبحث عن النصوص العادية
        searchPattern = new RegExp('(' + searchTerms.map(term => 
            term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // هروب من الأحرف الخاصة
        ).join('|') + ')', 'gi');
    }
    
    console.log('نوع البحث:', isNumericSearch ? 'أرقام' : 'نص');
    
    // العناصر التي نريد البحث فيها عن النص - استهداف عناصر محددة فقط داخل بطاقات التقارير
    // تعديل الاستهداف ليشمل فقط عناصر البيانات وليس التسميات
    const textElements = document.querySelectorAll('.report-card .card-body .info-item span:not(strong), .list-group-item span, td, .description-text');
    
    console.log('تم العثور على ' + textElements.length + ' عنصر للبحث فيه');
    
    // قائمة بالعناصر التي لا نريد إبرازها (مثل العناوين والتسميات)
    const excludedElements = ['strong', 'label', 'h5', 'h6', 'th'];
    
    // تطبيق الإبراز على كل عنصر
    textElements.forEach(element => {
        // تخطي العناصر التي ليست نصية أو التي تحتوي على عناصر HTML معقدة
        if (element.tagName === 'BUTTON' || element.tagName === 'A' || element.tagName === 'INPUT' || 
            element.classList.contains('search-highlight') || excludedElements.includes(element.tagName.toLowerCase())) {
            return;
        }
        
        // تخطي العناصر التي هي عناوين أو تسميات
        if (element.parentElement && excludedElements.includes(element.parentElement.tagName.toLowerCase())) {
            return;
        }
        
        // تخطي العناصر التي تحتوي على عناصر HTML أخرى (لتجنب تداخل التنسيق)
        if (element.children.length > 0) {
            // البحث في النصوص المباشرة فقط
            highlightTextNodes(element, searchPattern);
        } else {
            // الحصول على النص الأصلي
            const originalText = element.textContent;
            
            // استبدال النص المطابق بنفس النص ولكن مع إضافة span للتنسيق
            const highlightedText = originalText.replace(searchPattern, 
                '<span class="search-highlight">$1</span>'
            );
            
            // إذا تم العثور على تطابق، قم بتحديث المحتوى
            if (highlightedText !== originalText) {
                element.innerHTML = highlightedText;
                console.log('تم إبراز النص في العنصر:', element);
            }
        }
    });
    
    // دالة مساعدة لإبراز النص في عقد النص فقط
    function highlightTextNodes(element, pattern) {
        if (!element) return;
        
        try {
            // الحصول على جميع عقد الأبناء
            const childNodes = element.childNodes;
            
            // المرور على كل عقدة
            for (let i = 0; i < childNodes.length; i++) {
                const node = childNodes[i];
                
                // إذا كانت عقدة نص
                if (node.nodeType === Node.TEXT_NODE) {
                    // البحث عن النص المطابق
                    const text = node.textContent;
                    const matches = text.match(pattern);
                    
                    // إذا تم العثور على تطابق
                    if (matches) {
                        try {
                            // إنشاء عنصر span جديد
                            const highlightedText = text.replace(pattern, 
                                '<span class="search-highlight">$1</span>'
                            );
                            
                            // إنشاء عنصر مؤقت لتحويل النص إلى HTML
                            const tempElement = document.createElement('div');
                            tempElement.innerHTML = highlightedText;
                            
                            // استبدال عقدة النص بالعناصر الجديدة
                            const fragment = document.createDocumentFragment();
                            while (tempElement.firstChild) {
                                fragment.appendChild(tempElement.firstChild);
                            }
                            
                            // إدراج العناصر الجديدة قبل عقدة النص الحالية
                            element.insertBefore(fragment, node);
                            
                            // حذف عقدة النص الأصلية
                            element.removeChild(node);
                            
                            // تعديل المؤشر لمراعاة العناصر الجديدة المضافة
                            i += fragment.childNodes.length - 1;
                            
                            console.log('تم إبراز النص داخل عقدة نصية');
                        } catch (err) {
                            console.error('خطأ أثناء إبراز النص:', err);
                        }
                    }
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    // إذا كانت عقدة عنصر، قم بالبحث في أبنائها بشكل متكرر
                    // تجنب العناصر التي تم إبرازها بالفعل
                    if (!node.classList || !node.classList.contains('search-highlight')) {
                        highlightTextNodes(node, pattern);
                    }
                }
            }
        } catch (err) {
            console.error('خطأ في وظيفة highlightTextNodes:', err);
        }
    }
    
    // إضافة رسالة توضيحية عن عدد الكلمات التي تم إبرازها
    setTimeout(function() {
        const highlightedElements = document.querySelectorAll('.search-highlight');
        console.log('تم إبراز ' + highlightedElements.length + ' كلمة في نتائج البحث');
    }, 500);
});
