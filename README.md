# Mini-UPS

A full-stack web application modeling UPS delivery system paired with warehouse and an online-store system (like amazon). 
It simulated the whole process from receiving order to getting the package delivered. 
Frontend is developed with Django and backend is developed in Python. 
Google Protocol Buffer is used to communicate with world-simulator and mini amazon system partner.

author: Boyi Wang, Qiheng Gao

## Feature checklist(requirement)
* The	ability	to	enter	a	tracking	number	and	see	the	status of	the	shipment.	
* User accounts	(with	user ids	and	passwords).	If	you	are	logged	in,	you	should	be	able	to	do	the	
following	to	packages	you	own	(your	user	id	was	supplied	to	Amazon	when	the	purchase	was	
made):	
  * See	a	list	of	all	packages	that	belong	to	them.	
  * See	the	details	of	the	package	(e.g., items	inside	it)	
  * If	the	package	is	not	yet	out	for	delivery,	redirect	it	to	a	different	address.	(Note:	if	the	
user	loses	a	race	and	the	package	goes	out	for	delivery	before	you	can	update	it,	that	
is	OK,	but	you	need	to	tell	them	this).	

## Extra features we have:
* Require re-send if package lost.
* check(& uncheck) any orders you want
* A full-featured delivery management system + seller.
  * Customer will has his/her own tracking page
* Search bar in home page.
* view detail of any packages.
  * Including all time, location, real-time location details.
* Build-in data
  * use signals to make sure we have some build-in data(e.g. initial items, defualt user), easy to deploy
* Email notification.
  * we will send a confirmation email to user once package delivered.
* Edit user profile
  * a separate page to allow user edit his/her personal infromation(e.g. name, email, password)
* Associate your amazon account with your UPS account.
  * automatically associate each order with your UPS account
* User-friendly UI and interaction.
  * all edit info page will have some error handling, will show the error message if failed
  * use jQuery + aJax to make interaction more smooth
