

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;

/**
 * <p>Encapsulates our connection to the server, and provides convenience
 * methods that allow us to read and write lines of data.
 *
 * @version $Id: IRCConnection.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public class IRCConnection {
    public static final byte[] IRC_NEWLINE = new byte[]{ (byte) '\r', (byte) '\n' };
    private final String hostName;
    private final int port;
    private Socket socket;
    private BufferedReader in;
    private BufferedOutputStream out;
    private boolean open = false;

    public IRCConnection(String hostName, int port) {
        this.hostName = hostName;
        this.port = port;
    }

    /**
     * <p>Close the connection.
     */
    public void close() {
        if (socket != null)
            try {
                socket.close();
            } catch (IOException e) {
                System.err.println("[DEBUG] Error closing socket: " + e);
            }
        open = false;
    }

    /**
     * <p>Close the connection, sending one last line before the connection
     * is lost
     */
    public void close(String quitMessage) {
        if (open)
            try {
                sendLine("QUIT :" + quitMessage);
            } catch (IOException ioe) {
                // we really don't care much if this works or not
            }

        close();
    }

    /**
     * <p>Open the connection.
     */
    public void connect()
            throws java.net.UnknownHostException, IOException {
        if (open)
            throw new IllegalStateException("Trying to open an already open connection");

        socket = new Socket(hostName, port);
        in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        out = new BufferedOutputStream(socket.getOutputStream());
        open = true;
    }

    public String getServerHostName() {
        return hostName;
    }

    public int getServerPortNumber() {
        return port;
    }

    public boolean isOpen() {
        return open;
    }

    /**
     * <p>Read a line from the connection.
     */
    public String readLine() throws IOException {
        return in.readLine();
    }

    /**
     * <p>Will send a line to a server over the connection. This method automatically
     * appends the IRC-standard newline (\r\n) to the message, so you don't have to
     * worry about sticking it in the line to be sent.
     */
    public void sendLine(String line) throws IOException {
        if (!open)
            throw new IOException("Not connected to server");

        synchronized (out) {
            out.write(line.getBytes());
            out.write(IRC_NEWLINE);
        }
        out.flush();
    }
}
