var socket = io.connect('http://' + document.domain + ':' + location.port);

function UserViewModel() {
    var self = this;

    self.username = ko.observable('');
    self.currStatus = ko.observable(false);
    self.currDesc = ko.observable('');

    self.contacts = ko.observableArray([]);

    self.users = ko.observableArray([]);
    self.currSelectContact = ko.observableArray('');

    self.inRoom = ko.observable(false);
    self.currRoom = ko.observable('');
    self.currMsg = ko.observable('');

    self.messages = ko.observableArray([]);

    self.privateUser = ko.observable('');

    var section = $('.section');

    self.delUserContact = function delUserContact(data) {
        socket.emit('del_user', {'username': self.username(), 'del': data._id});
        self.contacts.remove(data);
        self.users.push(data._id);
    };

    self.changeStatus = function changeStatus() {
        socket.emit('status', {'username': self.username(), status: !self.currStatus()});
    };

    self.changeDesc = function changeDesc() {
        socket.emit('description', {'username': self.username(), description: self.currDesc()});
    };

    self.addUser = function addUser() {
        if (self.currSelectContact()) {
            $.ajax({
                type: "POST",
                url: "/contact/",
                data: JSON.stringify({ username: self.currSelectContact() }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    socket.emit('get_contacts');
                    socket.on('give_contacts', function (data) {
                        self.contacts(data.data);
                    });
                    self.users.remove(self.currSelectContact());
                }
            });
        }
    };

    self.joinRoom = function joinRoom(data) {
        if (!self.inRoom()) {
            self.currRoom(data);
            self.inRoom(true);
            socket.emit('join', {room: data});
        }
        else {
            self.currRoom(0);
            self.inRoom(false);
            socket.emit('leave', {room: data});
            self.messages([]);
        }
    };

    self.talkToUser = function talkToUser(data) {
        if (data._id === self.privateUser()) {
            leaveChat();
        }
        else {
            joinPrivateChat(data._id);
        }

        if (self.currRoom() !== '') {
            socket.emit('leave', {room: self.currRoom()});
        }
        self.messages([]);
    };

    function leaveChat() {
        self.inRoom(false);
        self.privateUser('');
        self.currRoom('');
    }

    function joinPrivateChat(userContactName) {
        self.inRoom(true);
        self.privateUser(userContactName);
        socket.emit('create_private_chat', {username: self.username(), contact: userContactName});
    }

    self.sendMsg = function sendMsg() {
        if (self.inRoom()) {
            socket.emit('room_msg', {username: self.username(), data: self.currMsg(), room: self.currRoom()});
            self.currMsg('');
        }
        else {
            alert('Please join one of the rooms.');
        }
    };

    socket.emit('give_user');
    socket.on('get_user', function (data) {
        self.username(data.username);
        self.currStatus(data.status);
        self.currDesc(data.description);

        var url = "/contact/" + self.username() + "/";

        $.getJSON(url, function (data) {
            self.users([]);
            self.users(data.data);
        });
    });

    socket.on('update_status', function () {
        get_contacts();
    });

    socket.on('msg', function (msg) {
        self.messages.push({'user': msg.user, 'message': msg.message});
        updateSection();
    });

    socket.on('private_chat', function (data) {
        socket.emit('join', {room: data.data.chat_id});
        self.currRoom(data.data.chat_id);
        self.messages(data.data.history);
        updateSection();
    });

    function updateSection() {
        section.scrollTop(section[0].scrollHeight);
    }

    get_contacts();

    function get_contacts() {
        socket.emit('get_contacts');
        socket.on('give_contacts', function (data) {
            self.contacts(data.data);
        });
    }
}

ko.applyBindings(new UserViewModel());

