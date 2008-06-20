

/**
 * @version $Id: PrivmsgStrategy.java,v 1.2 2003/12/02 22:08:20 bryan_w Exp $
 */
public class PrivmsgStrategy extends MessageStrategy {
    public java.lang.String decorateChannelMessage(java.lang.String source, java.lang.String message) {
        return "<" + source + "> " + message;
    }

    public java.lang.String decoratePrivateMessage(java.lang.String source, java.lang.String message) {
        return "*>" + source + "<* " + message;
    }

    public void doPing(String source, String message) {
        getSession().sendToUser("[P] " + source + " PING'ed you.");
        getSession().sendToServer(
                "NOTICE " + source + " :\001PING " + message.substring(6));
    }

    public void doVersion(String source, String message) {
        getSession().sendToUser("[C] " + source + " sent you a VERSION request");
        getSession().sendToServer("NOTICE " + source +
                " :\001VERSION SNirc_" + Chat.VERSION + " Java" + System.getProperty("java.version") + " cl00bie <cl00bie@sorcery.net>\001");
    }

    /**
     * <p>Register a Strategy with the Command object.
     * Strategies are responsible for telling the Command object
     * what commands they are interested in, using its registerStrategy()
     * method.
     */
    public void register() {
        Command.registerStrategy("PRIVMSG", this);
    }
}
