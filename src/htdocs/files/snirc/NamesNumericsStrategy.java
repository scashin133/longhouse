
import java.util.Enumeration;
import java.util.StringTokenizer;
import java.util.Vector;

/**
 * <p>Handles the numerics for NAMES replies and END OF NAMES. Will
 * cache the results of the NAMES replies, and then when END OF NAMES
 * is received, will update the channel names list in one big block.
 *
 * @version $Id: NamesNumericsStrategy.java,v 1.3 2004/07/22 18:24:07 bryan_w Exp $
 */
public class NamesNumericsStrategy implements CommandProcessingStrategy {
    public static final String NAMES_NUMERIC = "353";
    public static final String END_OF_NAMES_NUMERIC = "366";
    public static final String USERHOST_NUMERIC = "302";
    private Vector listedNicks = new java.util.Vector();
    

    private void doEndOfNames(Chat session) {
        session.clearNickList();
        Enumeration e = listedNicks.elements();
        while (e.hasMoreElements()) {
            String nick = (String) e.nextElement();
            if ((nick.charAt(0) == Chat.MODE_CHANOP)
                    || (nick.charAt(0) == Chat.MODE_VOICE))
                session.addToNickList(nick.substring(1), nick.charAt(0));
            else
                session.addToNickList(nick, Chat.MODE_NONE);
        }
        listedNicks = new Vector();
    }
    
    private String getNickHost(String nk){
    	String[] userhost = nk.split("@");
    	return 	userhost[userhost.length-1];
    }

    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */
    public void execute(Command command, Chat session) {
    	
        if (command.getCommand().equals(NAMES_NUMERIC)) {
            if (session.isCurrentChannel(command.getArgument(2))) {

                session.sendToUser(
                        "[N] "
                        + command.getArgument(2)
                        + " Channel Members: "
                        + command.getArgument(3));
                StringTokenizer nickList = new StringTokenizer(command.getArgument(3));
                while (nickList.hasMoreTokens()) {
                	String nxNick = nickList.nextToken();
                    listedNicks.addElement(nxNick);
                 
                }

            }
            return;
        }
        if (command.getCommand().equals(USERHOST_NUMERIC)) {
        	
        	session.setBanMask(getNickHost(command.getArguments()));
        }

        if (command.getCommand().equals(END_OF_NAMES_NUMERIC)) {
            doEndOfNames(session);
        }
    }

    /**
     * <p>Register this strategy with the Command object
     */
    public void register() {
        Command.registerStrategy(NAMES_NUMERIC, this);
        Command.registerStrategy(END_OF_NAMES_NUMERIC, this);
        Command.registerStrategy(USERHOST_NUMERIC, this);
    }
}
