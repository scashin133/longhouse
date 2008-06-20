

/**
 * <p>Strategy for handling the NICK command and related numeric
 * responses from the server.
 *
 * @version $Id: NickCommandsStrategy.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public class NickCommandsStrategy implements CommandProcessingStrategy {
    public static final String NICK_IN_USE_NUMERIC = "433";
    public static final String BAD_NICK_NUMERIC = "432";

    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */
    public void execute(Command command, Chat session) {
        if (command.getCommand().equals("NICK")) {
            session.sendToUser(
                    "[N] " + command.getSource() + " is now known as " + command.getArgument(0));
            if (session.isCurrentNick(command.getSource()))
                session.setNick(command.getArgument(0));
            String decoratedNick =
                    session.getDecoratedNickFromNickList(command.getSource());
            if (decoratedNick == null) {
                session.addToNickList(
                        command.getArgument(0),
                        Chat.MODE_NONE);
            } else {
                session.replaceOnNickList(
                        command.getSource(),
                        command.getArgument(0),
                        decoratedNick.charAt(0));
            }

        } else if (
                command.getCommand().equals(BAD_NICK_NUMERIC)
                || command.getCommand().equals(NICK_IN_USE_NUMERIC)) {
            session.sendToServer("NICK " + EntryDialog.promptForNick(command.getArgument(1) + ": " + command.getArgument(2)));
        }
    }

    /**
     * <p>Register a Strategy with the Command object.
     * Strategies are responsible for telling the Command object
     * what commands they are interested in, using its registerStrategy()
     * method.
     */
    public void register() {
        Command.registerStrategy("NICK", this);
        Command.registerStrategy(BAD_NICK_NUMERIC, this);
        Command.registerStrategy(NICK_IN_USE_NUMERIC, this);
    }
}
