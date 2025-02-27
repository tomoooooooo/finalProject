Documentatie Bookstore

1. Introducere

Aceasta este o aplicatie web pentru gestionarea unei librarii online, dezvoltata cu Flask si SQLite. Aplicatia permite utilizatorilor sa exploreze carti, sa le adauge in cos, sa le evalueze si sa finalizeze comenzile. Administratorii pot gestiona catalogul de carti.

2. Structura Proiectului
/bookstore
│── static/              # CSS, JS, imagini
│── templates/           # Pagini HTML
│── app.py               # Aplicatia principala
│── database.db          # Baza de date SQLite

3. Functionalitati

Autentificare si autorizare (User/Admin)

Vizualizare lista carti

Adaugare carti in cos si finalizare comanda

Evaluare carti

Cautare carti

Management carti (doar pentru admini)

4. Rute si Logica Aplicatiei

Autentificare

/login - autentificare utilizator

/register - creare cont

/logout - delogare

Carti

/books - lista tuturor cartilor

/book/<id> - detalii despre o carte

/add_book - adaugare carte (admin)

Cos de cumparaturi

/cart - afisare cos

/add_to_cart/<book_id> - adaugare carte in cos

/submit_order - finalizare comanda

5. Autentificare si Autorizare

Se foloseste Flask-Login pentru gestionarea autentificarii. Doar administratorii pot adauga carti.

6. Stilizare si Interfata

Fisierele CSS si JS sunt in static/. Aplicatia foloseste un design minimalist pentru claritate.

7. Concluzie si Posibile Imbunatatiri

Adaugarea unei metode de plata

Permiterea utilizatorului de a intra pe profilul sau si a vedea istoricul comenzilor

Adaugarea filtrelor de cautare pentru autor, interval de pret

Implementarea unui sistem de recenzii

Trimiterea unui email catre utilizator dupa plasarea comenzii