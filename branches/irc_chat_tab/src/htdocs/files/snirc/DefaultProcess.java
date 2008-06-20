

/**
 * <p>The command processing strategy that we use if no other command
 * in the list matches.
 *
 * <p>Currently contains all the spaghetti-code that was in the original
 * command parser, but that will be whittled down as each new processing
 * strategy is added.
 *
 * @version $Id: DefaultProcess.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public class DefaultProcess implements CommandProcessingStrategy {
    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */
    public void execute(Command command, Chat session) {
        if (Character.isDigit(command.getCommand().charAt(0))) {
            session.sendToUser("-" + command.getSource() + "- " + command.getArguments(1));
        } else {
            session.sendToUser("-" + command.getSource() + "- " + command.getArguments(0));
        }
    }

    public void register() {
        //noop
    }
}
