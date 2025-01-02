"""Interface which cloud receive command and send to remote server"""
from pexpect import pxssh


class RemoteServer:
    """
    This class allow user to build and store a ssh connection session.
    """
    pxssh_session = pxssh.pxssh
    exception_pxssh = pxssh.ExceptionPxssh

    def __init__(self, user: str, host: str, password: str = None, port: int = 22) -> None:
        self.user = user
        self.host = host
        self.port = port
        self.password = password
        self.session = self.pxssh_session()
        self.connected = False

    def _password_login(self, errors):
        """Login remote server with password
            put raise in errors
        """
        try:
            self.session.login(server=self.host, username=self.user, password=self.password, port=self.port)
        except self.exception_pxssh as e:
            errors.append(e.value)
        else:
            self.connected = True

    def _password_free_login(self, errors):
        """Login remote server without password
           put raise in errors
       """
        try:
            self.session.login(server=self.host, username=self.user, port=self.port)
        except self.exception_pxssh as e:
            errors.append(e.value)
        else:
            self.connected = True

    def _login(self) -> None:
        """
        Login with or without password
        raise if tried both way and failed
        """
        erros = []
        if self.password:
            self._password_login(erros)
        if not self.connected:
            self._password_free_login(erros)
        if len(erros) > 0 and not self.connected:
            raise self.exception_pxssh(erros)

    def _logout(self) -> None:
        """close connection"""
        self.session.logout()
        self.session.close()
        self.connected = False
        self.session = self.pxssh_session()

    def send_command(self, command) -> str:
        """
        send command to remote and return response
        """
        if not self.connected:
            self._login()
        self.session.sendline(command)
        self.session.prompt()
        text = self.session.before
        return text

    def __enter__(self):
        self._login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._logout()
