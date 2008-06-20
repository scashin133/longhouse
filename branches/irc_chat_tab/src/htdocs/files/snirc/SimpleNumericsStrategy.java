

/**
 * <p>Handles the numerics for anything that just requires minor text
 * rewriting and blatting to the outputPane. Currently handles replies
 * for:
 *
 * <ul>
 *     <li>PING/PONG
 *     <li>WHOIS
 *     <li>MOTD
 *     <li>TOPIC
 *	   <li>ERR_BANNEDFROMCHAN
 * </ul>
 *
 * @version $Id: SimpleNumericsStrategy.java,v 1.4 2004/07/26 18:24:58 bryan_w Exp $
 */
public class SimpleNumericsStrategy implements CommandProcessingStrategy {
    public static final String WHOIS_NUMERIC = "311";
    public static final String WHOIS_SERVER_NUMERIC = "312";
    public static final String WHOIS_IRCOP_NUMERIC = "313";
    public static final String WHOIS_IDLE_NUMERIC = "317";
    public static final String WHOIS_END_NUMERIC = "318";
    public static final String WHOIS_CHANNELS_NUMERIC = "319";
    public static final String TOPIC_IS_NUMERIC = "332";
    public static final String MOTD_NUMERIC = "372";
    public static final String END_OF_MOTD_NUMERIC = "376";
    public static final String MOTD_MISSING_NUMERIC = "422";
    public static final String UNKNOWN_COMMAND = "421";
    public static final String BANNED_NUMERIC = "474";

    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */
    public void execute(Command command, Chat session) {
        String reply = "";

        if (command.getCommand().equals(WHOIS_NUMERIC)) {
            reply = "[W] " + command.getArgument(1) + " is " + command.getArgument(2) + "@" + command.getArgument(3) + " (" + command.getArgument(5) + ")";
        } else if (command.getCommand().equals(BANNED_NUMERIC)){
        	session.sendToUser("[B] Cannot Join " + command.getArgument(1) + " address is banned");
        
        } else if (command.getCommand().equals("PING")) {
            session.sendToServer("PONG " + command.getArgument(0));
            if(ChatUserInterface.isDisplayingPingAndPong()) {
            	reply = "PING? PONG!";
            }
        } else if (command.getCommand().equals(WHOIS_SERVER_NUMERIC)) {
            reply = "[W] " + command.getArgument(1) + " is on server " + command.getArgument(2) + " (" + command.getArgument(3) + ")";
        } else if (command.getCommand().equals(WHOIS_IRCOP_NUMERIC)) {
            reply = "[W] " + command.getArgument(1) + " " + command.getArgument(2);
        } else if (command.getCommand().equals(WHOIS_IDLE_NUMERIC)) {
            reply = "[W] " + command.getArgument(1) + " has been idle " + secondsToString(command.getArgument(2));
        } else if (command.getCommand().equals(WHOIS_END_NUMERIC)) {
            reply = "[W] End of " + command.getArgument(1) + "'s Whois info";
        } else if (command.getCommand().equals(WHOIS_CHANNELS_NUMERIC)) {
            reply = "[W] " + command.getArgument(1) + " is on channel(s) " + command.getArgument(2);
        } else if (command.getCommand().equals(MOTD_NUMERIC)) {
            reply = command.getArgument(1);
        } else if (command.getCommand().equals("332")) {
            session.setChannelTopic("Topic: " + command.getArgument(2));
            reply = "[T] The topic on " + command.getArgument(1) + " is: " + command.getArgument(2);
        } else if (command.getCommand().equals("TOPIC")) {
            session.setChannelTopic("Topic: " + command.getArgument(1));
            reply = "[T] " + command.getSource() + " has changed the topic on " +
                    command.getArgument(0) + " to: " + command.getArgument(1);
        } else if (command.getCommand().equals(END_OF_MOTD_NUMERIC) || command.getCommand().equals(MOTD_MISSING_NUMERIC)) {
            session.serverConnectionIsActive();
        } else if (command.getCommand().equals(UNKNOWN_COMMAND)) {
        	reply = "[E] Unknown command - Type /help for instructions" ;
    	}
        session.sendToUser(reply);
    }

    /**
     * <p>Register a Strategy with the Command object.
     * Strategies are responsible for telling the Command object
     * what commands they are interested in, using its registerStrategy()
     * method.
     */
    public void register() {
        Command.registerStrategy(WHOIS_NUMERIC, this);
        Command.registerStrategy(WHOIS_END_NUMERIC, this);
        Command.registerStrategy(WHOIS_IDLE_NUMERIC, this);
        Command.registerStrategy(WHOIS_IRCOP_NUMERIC, this);
        Command.registerStrategy(WHOIS_CHANNELS_NUMERIC, this);
        Command.registerStrategy(WHOIS_SERVER_NUMERIC, this);
        Command.registerStrategy(MOTD_NUMERIC, this);
        Command.registerStrategy(END_OF_MOTD_NUMERIC, this);
        Command.registerStrategy(MOTD_MISSING_NUMERIC, this);
        Command.registerStrategy(TOPIC_IS_NUMERIC, this);
        Command.registerStrategy("PING", this);
        Command.registerStrategy("TOPIC", this);
        Command.registerStrategy(BANNED_NUMERIC, this);
    }

    private String secondsToString(String secondsString) {
        int seconds;
        try {
            seconds = Integer.parseInt(secondsString);
        } catch (NumberFormatException nfe) {
            return secondsString;
        }

        StringBuffer response = new StringBuffer();
        if (seconds > 24 * 60 * 60) {
            int days = seconds / 24 * 60 * 60;
            if (days == 1) {
                response.append("1 day, ");
            } else {
                response.append(days + " days, ");
            }
            seconds -= days * 24 * 60 * 60;
        }

        if (seconds > 60 * 60) {
            int hours = seconds / 60 * 60;
            if (hours == 1) {
                response.append("1 hour, ");
            } else {
                response.append(hours + " hours, ");
            }
            seconds -= hours * 60 * 60;
        }

        if (seconds > 60) {
            int minutes = seconds / 60;
            if (minutes == 1) {
                response.append("1 minute, ");
            } else {
                response.append(minutes + " minutes, ");
            }
            seconds -= minutes * 60;
        }

        if (seconds == 1) {
            response.append("1 second");
        } else {
            response.append(seconds + " seconds");
        }
        return response.toString();
    }
}
