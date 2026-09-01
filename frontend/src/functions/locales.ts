export type Language = 'ar' | 'en';

export const translations = {
  ar: {
    // نصوص NavBar
    home: 'الرئيسية',
    newChat: 'محادثة جديدة',
    chats: 'المحادثات',
    workflows: 'سير العمل',
    lightMode: 'فاتح',
    darkMode: 'داكن',
    appTitle: 'إطار الوكلاء',
    appSubtitle: 'منشئ الأكواد',
    navSection: 'التنقل',
    
    // نصوص صفحات وكلاء ومحادثات أخرى يمكن إضافتها لاحقاً
    agentsEmptyTitle: 'لا يوجد محادثات / وكلاء بعد',
    agentsCount: 'عدد الوكلاء:',
  },
  en: {
    // NavBar texts
    home: 'Home',
    newChat: 'New Chat',
    chats: 'Chats',
    workflows: 'Workflows',
    lightMode: 'Light',
    darkMode: 'Dark',
    appTitle: 'Agents Framework',
    appSubtitle: 'Code Generator',
    navSection: 'Navigation',
    
    // Other texts
    agentsEmptyTitle: 'No chats / agents yet',
    agentsCount: 'Agents count:',
  }
};