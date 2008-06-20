

/**
 * @version $Id: NoticeStrategy.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public class NoticeStrategy extends MessageStrategy {
    public java.lang.String decorateChannelMessage(java.lang.String source, java.lang.String message) {
        return "-" + source + ":" + getSession().getChannelName() + "- " + message;
    }

    public java.lang.String decoratePrivateMessage(java.lang.String source, java.lang.String message) {
        return "-" + source + "-" + message;
    }

    public void doPing(String source, String message) {
        try {
            getSession().sendToUser(
                    "[P] Ping reply from "
                    + source
                    + " is "
                    + (System.currentTimeMillis()
                    - Long.parseLong(message.substring(6, message.length() - 1).trim()))
                    / 1000
                    + " seconds.");
        } catch (NumberFormatException e) {
        }
    }

    public void doVersion(String source, String message) {
        getSession().sendToUser(
                "[V] " + source + " is using " + message.substring(7).replace('\001', ' '));
    }

    /**
     * <p>Register a Strategy with the Command object.
     * Strategies are responsible for telling the Command object
     * what commands they are interested in, using its registerStrategy()
     * method.
     */
    public void register() {
        Command.registerStrategy("NOTICE", this);
    }
}
